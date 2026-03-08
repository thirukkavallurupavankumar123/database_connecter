import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.models.models import DatabaseConnection, QueryHistory, SchemaCache, User, Organization
from app.schemas.schemas import (
    QueryRequest, QueryResponse, ReportRequest, QueryHistoryResponse,
    ConnectRequest, ConnectResponse,
)
from app.services.database_connector import get_client_engine
from app.services.schema_extractor import schema_to_prompt_context
from app.services.sql_validator import validate_sql, SQLValidationError
from app.services.query_executor import execute_readonly_query
from app.services.data_processor import compute_statistics, detect_trends
from app.services.report_generator import generate_csv, generate_excel, generate_json_report, generate_pdf
from app.agents.query_agent import generate_sql
from app.agents.analysis_agent import analyze_data

router = APIRouter(prefix="/api/query", tags=["Query & Analysis"])


@router.post("/connect", response_model=ConnectResponse)
def connect_session(payload: ConnectRequest, db: Session = Depends(get_db)):
    """Validate user and return their available database connections."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Active user not found")

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    connections = db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == user.organization_id,
        DatabaseConnection.is_active == True,
    ).all()

    return ConnectResponse(
        user_id=user.id,
        user_name=user.name,
        organization_id=org.id,
        organization_name=org.name,
        connections=connections,
    )


@router.post("/", response_model=QueryResponse)
def run_query(payload: QueryRequest, db: Session = Depends(get_db)):
    """Full pipeline: NL query → SQL → execute → analyze → return results."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Active user not found")

    # 1. Load connection
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == payload.connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if conn.organization_id != user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="This user is not allowed to query the selected connection",
        )

    # 2. Load schema context
    cache = db.query(SchemaCache).filter(
        SchemaCache.connection_id == conn.id
    ).first()
    if not cache:
        raise HTTPException(status_code=400, detail="Schema not cached. Refresh schema first.")

    tables = json.loads(cache.schema_json)
    schema_context = schema_to_prompt_context(tables)

    # 3. Create query history record
    history = QueryHistory(
        user_id=payload.user_id,
        connection_id=conn.id,
        natural_language_query=payload.natural_language_query,
        status="pending",
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    # 3b. Keep only the latest 10 history records per user
    MAX_HISTORY = 10
    user_history = db.query(QueryHistory).filter(
        QueryHistory.user_id == payload.user_id
    ).order_by(QueryHistory.created_at.desc()).all()
    if len(user_history) > MAX_HISTORY:
        for old_record in user_history[MAX_HISTORY:]:
            db.delete(old_record)
        db.commit()

    try:
        # 4. AI Agent 1: Generate SQL
        sql = generate_sql(
            natural_language_query=payload.natural_language_query,
            schema_context=schema_context,
            db_type=conn.db_type,
        )

        # 5. Validate SQL safety
        validated_sql = validate_sql(sql)

        # 6. Execute query on client database
        engine = get_client_engine(
            db_type=conn.db_type, host=conn.host, port=conn.port,
            database_name=conn.database_name, username=conn.username,
            encrypted_password=conn.encrypted_password, ssl_enabled=conn.ssl_enabled,
        )
        try:
            columns, data = execute_readonly_query(engine, validated_sql)
        finally:
            engine.dispose()

        # 7. Data processing: statistics & trends
        statistics = compute_statistics(columns, data)
        trends = detect_trends(columns, data)

        # 8. AI Agent 2: Generate analysis
        analysis = analyze_data(
            natural_language_query=payload.natural_language_query,
            columns=columns,
            data=data,
            statistics=statistics,
            trends=trends,
        )

        # 9. Update history
        history.generated_sql = validated_sql
        history.status = "success"
        history.row_count = str(len(data))
        conn.last_used_at = datetime.utcnow()
        db.commit()

        return QueryResponse(
            query_id=history.id,
            natural_language_query=payload.natural_language_query,
            generated_sql=validated_sql,
            columns=columns,
            data=data,
            row_count=len(data),
            statistics=statistics,
            ai_summary=analysis.get("summary", ""),
            ai_insights=analysis.get("insights", []),
        )

    except SQLValidationError as e:
        history.status = "error"
        history.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=f"SQL validation failed: {e}")

    except Exception as e:
        history.status = "error"
        history.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")


@router.post("/download")
def download_report(payload: ReportRequest, db: Session = Depends(get_db)):
    """Run query and return results as a downloadable file."""
    # Run the full pipeline first
    query_payload = QueryRequest(
        connection_id=payload.connection_id,
        user_id=payload.user_id,
        natural_language_query=payload.natural_language_query,
    )
    result = run_query(query_payload, db)

    fmt = payload.format.lower()
    if fmt == "csv":
        content = generate_csv(result.columns, result.data)
        media_type = "text/csv"
        filename = "report.csv"
    elif fmt == "excel":
        content = generate_excel(result.columns, result.data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "report.xlsx"
    elif fmt == "json":
        content = generate_json_report(
            result.columns, result.data, result.statistics, result.ai_summary
        )
        media_type = "application/json"
        filename = "report.json"
    elif fmt == "pdf":
        content = generate_pdf(
            result.columns, result.data,
            summary=result.ai_summary,
            title=result.natural_language_query,
        )
        media_type = "application/pdf"
        filename = "report.pdf"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/history/{user_id}", response_model=list[QueryHistoryResponse])
def get_query_history(user_id: str, db: Session = Depends(get_db)):
    """Get query history for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Active user not found")

    return db.query(QueryHistory).filter(
        QueryHistory.user_id == user_id
    ).order_by(QueryHistory.created_at.desc()).limit(10).all()

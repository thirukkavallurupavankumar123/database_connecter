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
from app.agents.router_agent import select_connection_with_agent

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


def _select_connection_for_query(payload: QueryRequest, user: User, db: Session) -> DatabaseConnection:
     """Auto-select a connection when none is provided.

     Priority:
     1. Explicit connection_id from payload (validated).
     2. If multiple connections and no id, use AI routing agent to pick the
         best connection based on labels, tags, and organization context.
     3. If the agent fails for any reason, fall back to simple keyword routing
         with default connection preference.
     """
    if payload.connection_id:
        conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == payload.connection_id).first()
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found")
        if conn.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="This user is not allowed to query the selected connection")
        return conn

    # No connection_id provided — auto route within the org
    org_connections = db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == user.organization_id,
        DatabaseConnection.is_active == True,
    ).all()

    if not org_connections:
        raise HTTPException(status_code=400, detail="No active connections configured for this organization")
    if len(org_connections) == 1:
        return org_connections[0]

    # Prefer explicit default (used by both AI router and fallback heuristic)
    default_conn = next((c for c in org_connections if c.is_default), None)

    # Try AI-based routing first for enterprise-grade selection
    try:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()

        connections_payload = [
            {
                "id": c.id,
                "name": c.name,
                "label": c.label,
                "tags": c.tags,
                "db_type": c.db_type,
                "is_default": bool(c.is_default),
            }
            for c in org_connections
        ]

        router_result = select_connection_with_agent(
            natural_language_query=payload.natural_language_query,
            connections=connections_payload,
            organization_name=org.name if org else None,
            default_connection_id=default_conn.id if default_conn else None,
        )

        selected_id = router_result.get("connection_id")
        if isinstance(selected_id, str):
            selected = next((c for c in org_connections if c.id == selected_id), None)
            if selected is not None:
                return selected
    except Exception:
        # Fall back to heuristic routing below
        pass

    # Fallback: simple keyword routing matching query words against name/label/tags
    tokens = [t for t in payload.natural_language_query.lower().replace("\n", " ").split(" ") if t]

    def score(conn: DatabaseConnection) -> int:
        haystack = " ".join(filter(None, [conn.name, conn.label, conn.tags or ""]))
        haystack = haystack.lower()
        return sum(1 for t in tokens if t in haystack)

    scored = sorted(
        ((c, score(c)) for c in org_connections),
        key=lambda item: item[1],
        reverse=True,
    )

    top_conn, top_score = scored[0]
    if top_score == 0:
        if default_conn:
            return default_conn
        # Ambiguous: ask client to specify
        options = [f"{c.name} ({c.db_type})" for c in org_connections]
        raise HTTPException(
            status_code=400,
            detail=f"Multiple databases available. Please pick one: {', '.join(options)}",
        )

    # If tie at top and a default exists among them, prefer default
    best_conns = [c for c, s in scored if s == top_score]
    if default_conn and default_conn in best_conns:
        return default_conn

    return top_conn


@router.post("/", response_model=QueryResponse)
def run_query(payload: QueryRequest, db: Session = Depends(get_db)):
    """Full pipeline: NL query → SQL → execute → analyze → return results."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Active user not found")

    # 1. Select connection (explicit or auto-route)
    conn = _select_connection_for_query(payload, user, db)

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

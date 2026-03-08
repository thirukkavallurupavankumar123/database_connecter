import io
import json
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_csv(columns: list[str], data: list[dict]) -> bytes:
    """Generate a CSV file from query results."""
    df = pd.DataFrame(data, columns=columns)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_excel(columns: list[str], data: list[dict]) -> bytes:
    """Generate an Excel file from query results."""
    df = pd.DataFrame(data, columns=columns)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Query Results")
    return buffer.getvalue()


def generate_json_report(columns: list[str], data: list[dict],
                         statistics: dict = None, summary: str = None) -> bytes:
    """Generate a JSON report with data, statistics, and AI summary."""
    report = {
        "columns": columns,
        "data": data,
        "row_count": len(data),
    }
    if statistics:
        report["statistics"] = statistics
    if summary:
        report["ai_summary"] = summary
    return json.dumps(report, indent=2, default=str).encode("utf-8")


def generate_pdf(columns: list[str], data: list[dict],
                 summary: str = None, title: str = "Query Report") -> bytes:
    """Generate a PDF report from query results."""
    buffer = io.BytesIO()
    page_size = landscape(letter) if len(columns) > 5 else letter
    doc = SimpleDocTemplate(buffer, pagesize=page_size)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    # AI Summary
    if summary:
        elements.append(Paragraph("AI Summary", styles["Heading2"]))
        elements.append(Paragraph(summary, styles["Normal"]))
        elements.append(Spacer(1, 12))

    # Data table (limit rows for PDF readability)
    display_data = data[:100]
    table_data = [columns]
    for row in display_data:
        table_data.append([str(row.get(col, "")) for col in columns])

    if table_data:
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t)

    if len(data) > 100:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"Showing 100 of {len(data)} rows.", styles["Italic"]
        ))

    doc.build(elements)
    return buffer.getvalue()

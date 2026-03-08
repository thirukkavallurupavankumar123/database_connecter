from pathlib import Path
from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "ARGO_Project_File_Explanation.pdf"


FILE_ENTRIES = [
    {
        "path": "README.md",
        "section": "Project Overview",
        "title": "Project documentation",
        "explanation": (
            "This file is the top-level project guide. It explains the platform goals, "
            "architecture, stack, security model, API surface, and the local setup steps. "
            "It is the first document a new engineer should read before opening the code."
        ),
        "snippet": (1, 40),
    },
    {
        "path": ".gitignore",
        "section": "Project Overview",
        "title": "Ignored files",
        "explanation": (
            "This file prevents virtual environments, build outputs, secrets, local databases, "
            "and editor-specific files from being committed. It keeps the repository clean and safe."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "backend/requirements.txt",
        "section": "Backend",
        "title": "Python dependencies",
        "explanation": (
            "This file declares the backend runtime dependencies. It includes FastAPI for APIs, "
            "SQLAlchemy for database access, Pandas and NumPy for analytics, Groq for the LLM calls, "
            "and ReportLab/openpyxl for report exports."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "backend/Dockerfile",
        "section": "Backend",
        "title": "Backend container",
        "explanation": (
            "This Dockerfile packages the FastAPI service for deployment. It installs the backend "
            "dependencies, copies the application code, exposes port 8000, and starts uvicorn."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "backend/.env.example",
        "section": "Backend",
        "title": "Backend environment template",
        "explanation": (
            "This file shows which environment variables the backend expects: Groq credentials, "
            "encryption key, frontend URL, database URL, and debug flag. It acts as a safe template "
            "for creating a local .env file."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "backend/app/__init__.py",
        "section": "Backend",
        "title": "Backend package marker",
        "explanation": (
            "This is the package marker for the backend app module. It allows Python to treat the "
            "app directory as an importable package."
        ),
        "snippet": None,
    },
    {
        "path": "backend/app/config.py",
        "section": "Backend",
        "title": "Central configuration",
        "explanation": (
            "This file defines the Settings object using pydantic-settings. It centralizes application "
            "name, Groq configuration, encryption keys, CORS origin, row limits, query timeout, and the "
            "internal metadata database URL. The get_settings function caches configuration reads."
        ),
        "snippet": (1, 80),
    },
    {
        "path": "backend/app/database.py",
        "section": "Backend",
        "title": "Internal metadata database session",
        "explanation": (
            "This file creates the SQLAlchemy engine and session factory used by the backend itself. "
            "It is separate from client databases. The get_db generator is injected into FastAPI routes "
            "so each request gets a clean session."
        ),
        "snippet": (1, 60),
    },
    {
        "path": "backend/app/main.py",
        "section": "Backend",
        "title": "FastAPI entry point",
        "explanation": (
            "This file starts the backend application. It creates internal tables, enables CORS for the "
            "frontend, registers all API routers, and exposes a root endpoint and a health endpoint."
        ),
        "snippet": (1, 80),
    },
    {
        "path": "backend/app/models/__init__.py",
        "section": "Backend",
        "title": "Models package marker",
        "explanation": (
            "This empty file marks the models directory as a Python package."
        ),
        "snippet": None,
    },
    {
        "path": "backend/app/models/models.py",
        "section": "Backend",
        "title": "Core data model",
        "explanation": (
            "This file defines the main SQLAlchemy tables for the platform. Organization and User support multi-tenancy. "
            "DatabaseConnection stores encrypted client connection details. SchemaCache stores discovered table metadata. "
            "QueryHistory tracks every natural-language query, generated SQL, status, and row count for auditability."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "backend/app/schemas/__init__.py",
        "section": "Backend",
        "title": "Schemas package marker",
        "explanation": "This empty file marks the schemas directory as a Python package.",
        "snippet": None,
    },
    {
        "path": "backend/app/schemas/schemas.py",
        "section": "Backend",
        "title": "Request and response schemas",
        "explanation": (
            "This file contains the Pydantic models used by the API layer. It validates incoming payloads such as "
            "organization creation, user creation, database connection input, query requests, and report downloads. "
            "It also standardizes API responses returned to the frontend."
        ),
        "snippet": (1, 140),
    },
    {
        "path": "backend/app/api/__init__.py",
        "section": "Backend APIs",
        "title": "API package marker",
        "explanation": "This empty file marks the api directory as a Python package.",
        "snippet": None,
    },
    {
        "path": "backend/app/api/organizations.py",
        "section": "Backend APIs",
        "title": "Organization and user API",
        "explanation": (
            "This router handles organization and user management. It creates organizations, lists them, reads a single "
            "organization, creates users inside an organization, and lists users by organization."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "backend/app/api/connections.py",
        "section": "Backend APIs",
        "title": "Database connection API",
        "explanation": (
            "This router manages client database connections. It can test credentials, save encrypted connection details, "
            "extract and cache schema metadata, list connections for an organization, and delete stale connections. "
            "It is the bridge between a tenant and their external database."
        ),
        "snippet": (1, 200),
    },
    {
        "path": "backend/app/api/queries.py",
        "section": "Backend APIs",
        "title": "Natural-language query pipeline API",
        "explanation": (
            "This is the core business route of the platform. It loads a saved connection, loads the cached schema, sends the "
            "user question to the query-generation agent, validates the SQL for safety, executes the query, computes statistics, "
            "sends the results to the analysis agent, stores history, and returns the final payload to the frontend."
        ),
        "snippet": (1, 220),
    },
    {
        "path": "backend/app/services/__init__.py",
        "section": "Backend Services",
        "title": "Services package marker",
        "explanation": "This empty file marks the services directory as a Python package.",
        "snippet": None,
    },
    {
        "path": "backend/app/services/encryption.py",
        "section": "Backend Services",
        "title": "Credential encryption",
        "explanation": (
            "This file encrypts and decrypts client database passwords using Fernet. The intent is that plaintext credentials "
            "are accepted only at connection setup time and are stored encrypted afterward."
        ),
        "snippet": (1, 80),
    },
    {
        "path": "backend/app/services/database_connector.py",
        "section": "Backend Services",
        "title": "Client database connector",
        "explanation": (
            "This service converts saved connection metadata into a SQLAlchemy URL, creates an engine for the client database, "
            "and provides a connection test helper. It currently supports PostgreSQL, MySQL, and SQL Server."
        ),
        "snippet": (1, 160),
    },
    {
        "path": "backend/app/services/schema_extractor.py",
        "section": "Backend Services",
        "title": "Schema discovery",
        "explanation": (
            "This service introspects client tables and columns using SQLAlchemy's inspector. It builds a normalized schema object "
            "and a prompt-friendly text representation that the LLM uses to generate accurate SQL."
        ),
        "snippet": (1, 160),
    },
    {
        "path": "backend/app/services/sql_validator.py",
        "section": "Backend Services",
        "title": "SQL safety validator",
        "explanation": (
            "This file is a core security control. It rejects empty SQL, anything that does not start with SELECT or WITH, any blocked "
            "keywords such as DELETE or DROP, multi-statement attempts, and SQL comments that could hide malicious instructions."
        ),
        "snippet": (1, 160),
    },
    {
        "path": "backend/app/services/query_executor.py",
        "section": "Backend Services",
        "title": "Read-only query execution",
        "explanation": (
            "This service executes validated SQL against the client database. It applies a row cap and attempts to set per-query timeouts "
            "where the database dialect allows it. The result is returned as column names and rows."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "backend/app/services/data_processor.py",
        "section": "Backend Services",
        "title": "Statistics and trend detection",
        "explanation": (
            "This file converts raw query rows into a Pandas DataFrame, then computes descriptive statistics for numeric and categorical columns. "
            "It also does a simple first-half versus second-half comparison to surface basic trends."
        ),
        "snippet": (1, 180),
    },
    {
        "path": "backend/app/services/report_generator.py",
        "section": "Backend Services",
        "title": "Report export service",
        "explanation": (
            "This service converts query output into CSV, Excel, JSON, and PDF bytes. It is used by the download endpoint so the UI can export "
            "analysis results in different formats."
        ),
        "snippet": (1, 220),
    },
    {
        "path": "backend/app/agents/__init__.py",
        "section": "AI Agents",
        "title": "Agents package marker",
        "explanation": "This empty file marks the agents directory as a Python package.",
        "snippet": None,
    },
    {
        "path": "backend/app/agents/query_agent.py",
        "section": "AI Agents",
        "title": "Agent 1: natural language to SQL",
        "explanation": (
            "This file wraps the Groq client for SQL generation. The system prompt is very restrictive: it tells the model to produce read-only SQL, "
            "use the given schema exactly, avoid markdown, avoid SELECT *, and use grouping and limits when needed."
        ),
        "snippet": (1, 160),
    },
    {
        "path": "backend/app/agents/analysis_agent.py",
        "section": "AI Agents",
        "title": "Agent 2: data to business insights",
        "explanation": (
            "This file sends a preview of the query result plus computed statistics and trend hints to Groq. The agent is asked to return a structured "
            "summary, a list of insights, and a list of trends that can be rendered in the UI."
        ),
        "snippet": (1, 220),
    },
    {
        "path": "frontend/package.json",
        "section": "Frontend",
        "title": "Frontend dependencies and scripts",
        "explanation": (
            "This file defines the frontend runtime and development dependencies. It includes Next.js, React, Chart.js, axios, TypeScript, Tailwind, "
            "and the standard build, dev, and lint scripts."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "frontend/Dockerfile",
        "section": "Frontend",
        "title": "Frontend container",
        "explanation": (
            "This Dockerfile builds the Next.js app in one stage and runs the standalone production server in another stage. "
            "That keeps the deployment image smaller and production-focused."
        ),
        "snippet": (1, 80),
    },
    {
        "path": "frontend/next.config.js",
        "section": "Frontend",
        "title": "Next.js build configuration",
        "explanation": (
            "This file enables standalone output so the frontend can be deployed with the minimal runtime files needed by the production server."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "frontend/tsconfig.json",
        "section": "Frontend",
        "title": "TypeScript configuration",
        "explanation": (
            "This file defines how the frontend is type-checked. It turns on strict mode, enables the Next.js plugin, and adds the @ alias for imports from src."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "frontend/tailwind.config.js",
        "section": "Frontend",
        "title": "Tailwind design configuration",
        "explanation": (
            "This file tells Tailwind where to scan for class names and extends the theme with a blue primary color scale used by the dashboard."
        ),
        "snippet": (1, 80),
    },
    {
        "path": "frontend/postcss.config.js",
        "section": "Frontend",
        "title": "PostCSS configuration",
        "explanation": (
            "This file enables Tailwind CSS and Autoprefixer during the frontend build."
        ),
        "snippet": (1, 40),
    },
    {
        "path": "frontend/src/app/globals.css",
        "section": "Frontend",
        "title": "Global styles",
        "explanation": (
            "This file loads Tailwind's base layers and defines the global dark-theme variables for background, cards, inputs, text, and scrollbars."
        ),
        "snippet": (1, 120),
    },
    {
        "path": "frontend/src/app/layout.tsx",
        "section": "Frontend",
        "title": "Application shell",
        "explanation": (
            "This file defines the global page layout. It contains the sidebar navigation and the main content area, so every page shares a common shell."
        ),
        "snippet": (1, 180),
    },
    {
        "path": "frontend/src/app/page.tsx",
        "section": "Frontend Pages",
        "title": "Dashboard page",
        "explanation": (
            "This landing page explains the platform at a glance. It gives the user a hero section, quick-start cards, and a feature grid."
        ),
        "snippet": (1, 180),
    },
    {
        "path": "frontend/src/app/connections/page.tsx",
        "section": "Frontend Pages",
        "title": "Connections page",
        "explanation": (
            "This page lets a tenant input an organization ID, test a client database connection, save it, load saved connections, and delete them. "
            "It is the main UI for onboarding external databases."
        ),
        "snippet": (1, 260),
    },
    {
        "path": "frontend/src/app/query/page.tsx",
        "section": "Frontend Pages",
        "title": "Query page",
        "explanation": (
            "This is the main user workflow page. The user enters a connection ID, user ID, and a natural-language question. The page calls the backend, shows the generated SQL, renders the AI summary, toggles between table and chart views, and supports downloads."
        ),
        "snippet": (1, 260),
    },
    {
        "path": "frontend/src/app/history/page.tsx",
        "section": "Frontend Pages",
        "title": "History page",
        "explanation": (
            "This page loads the last 50 query executions for a user. It displays the natural-language prompt, generated SQL, success or error status, and timestamps."
        ),
        "snippet": (1, 200),
    },
    {
        "path": "frontend/src/components/DataTable.tsx",
        "section": "Frontend Components",
        "title": "Tabular result renderer",
        "explanation": (
            "This component renders query output in a horizontally scrollable table. It uses the column list supplied by the backend and formats nulls and numbers for display."
        ),
        "snippet": (1, 180),
    },
    {
        "path": "frontend/src/components/ChartView.tsx",
        "section": "Frontend Components",
        "title": "Chart renderer",
        "explanation": (
            "This component turns tabular result data into bar, line, or pie charts using Chart.js. The user can choose which column acts as labels and which acts as values."
        ),
        "snippet": (1, 260),
    },
    {
        "path": "frontend/src/components/AiInsights.tsx",
        "section": "Frontend Components",
        "title": "AI summary card",
        "explanation": (
            "This component displays the business-facing text generated by the analysis agent. It separates the main summary from bullet insights."
        ),
        "snippet": (1, 140),
    },
    {
        "path": "frontend/src/lib/api.ts",
        "section": "Frontend Components",
        "title": "Frontend API client",
        "explanation": (
            "This file centralizes all frontend HTTP calls. It creates an axios client using NEXT_PUBLIC_API_URL and wraps each backend route in a small helper function."
        ),
        "snippet": (1, 220),
    },
]


def read_snippet(relative_path: str, line_range: tuple[int, int] | None) -> str:
    file_path = ROOT / relative_path
    if not file_path.exists():
        return "File not found when PDF was generated."
    if line_range is None:
        return "Package marker file. No runtime logic is defined here."

    start, end = line_range
    lines = file_path.read_text(encoding="utf-8").splitlines()
    start_index = max(0, start - 1)
    end_index = min(len(lines), end)
    selected = lines[start_index:end_index]
    numbered = [f"{start_index + idx + 1:>4}: {line}" for idx, line in enumerate(selected)]
    return "\n".join(numbered) if numbered else "File is empty."


def grouped_entries() -> list[tuple[str, list[dict]]]:
    order = []
    buckets: dict[str, list[dict]] = {}
    for entry in FILE_ENTRIES:
        section = entry["section"]
        if section not in buckets:
            buckets[section] = []
            order.append(section)
        buckets[section].append(entry)
    return [(section, buckets[section]) for section in order]


def build_pdf() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.textColor = colors.HexColor("#123b63")
    h1 = styles["Heading1"]
    h1.textColor = colors.HexColor("#123b63")
    h2 = styles["Heading2"]
    h2.textColor = colors.HexColor("#184e77")
    body = styles["BodyText"]
    body.leading = 15
    body.spaceAfter = 8
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=9,
        textColor=colors.HexColor("#4a5568"),
        leading=12,
    )
    code = ParagraphStyle(
        "CodeLabel",
        parent=body,
        fontSize=9,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=6,
        spaceAfter=4,
    )
    code_block = ParagraphStyle(
        "CodeBlock",
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#111827"),
        backColor=colors.HexColor("#f3f4f6"),
        borderColor=colors.HexColor("#d1d5db"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=10,
    )

    story = []
    story.append(Paragraph("ARGO Analytics: File-by-File Code Explanation", title_style))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "This PDF explains the structure of the project, the purpose of each source file, and the most important code inside each file. "
            "The goal is to make the codebase understandable end to end for implementation, review, and onboarding.",
            body,
        )
    )
    story.append(
        Paragraph(
            f"Repository root: {escape(str(ROOT))}",
            small,
        )
    )
    story.append(Spacer(1, 8))

    for section, entries in grouped_entries():
        story.append(Paragraph(section, h1))
        story.append(Spacer(1, 4))
        for entry in entries:
            story.append(Paragraph(f"{entry['path']} - {entry['title']}", h2))
            story.append(Paragraph(entry["explanation"], body))
            story.append(Paragraph("Representative code", code))
            snippet = read_snippet(entry["path"], entry["snippet"])
            story.append(Preformatted(snippet, code_block))
        story.append(PageBreak())

    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    pdf_path = build_pdf()
    print(pdf_path)
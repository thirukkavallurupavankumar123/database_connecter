# 🚀 ARGO Analytics — Enterprise GenAI Database Analytics Platform

AI-powered enterprise analytics platform where organizations connect their databases and analyze data using **natural language queries**. No SQL knowledge required.

## Architecture

```
User Browser
     │
     ▼
Frontend (Next.js / Vercel)
     │
     ▼
Backend API (FastAPI / Render)
     │
     ├── Groq AI (Agent 1: SQL Gen, Agent 2: Analysis)
     └── Client Database (PostgreSQL / MySQL / SQL Server)
```

## Features

- **Natural Language Queries** — Ask questions like "Show total revenue in 2024"
- **Auto SQL Generation** — AI Agent converts questions to SQL
- **Multi-Database Support** — PostgreSQL, MySQL, SQL Server
- **AI-Generated Insights** — Summaries, trends, and recommendations
- **Statistical Analysis** — Mean, median, std dev, distributions
- **Interactive Charts** — Bar, line, pie charts with Chart.js
- **Downloadable Reports** — CSV, Excel, JSON, PDF
- **Secure Read-Only Access** — SQL validation blocks all write operations
- **Multi-Tenant** — Organizations and users are fully isolated
- **Encrypted Credentials** — AES/Fernet encryption for database passwords

## Project Structure

```
ARGO_project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # Internal DB session
│   │   ├── models/models.py     # SQLAlchemy models
│   │   ├── schemas/schemas.py   # Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── organizations.py # Org & user management endpoints
│   │   │   ├── connections.py   # DB connection CRUD & schema extraction
│   │   │   └── queries.py       # NL query → SQL → execute → analyze
│   │   ├── services/
│   │   │   ├── encryption.py        # AES credential encryption
│   │   │   ├── database_connector.py # Client DB engine builder
│   │   │   ├── schema_extractor.py   # Table/column metadata extraction
│   │   │   ├── sql_validator.py      # Read-only SQL safety checks
│   │   │   ├── query_executor.py     # Safe query execution with limits
│   │   │   ├── data_processor.py     # Pandas/NumPy statistics
│   │   │   └── report_generator.py   # CSV/Excel/JSON/PDF generation
│   │   └── agents/
│   │       ├── query_agent.py    # Agent 1: NL → SQL via Groq
│   │       └── analysis_agent.py # Agent 2: Data → Insights via Groq
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout with sidebar
│   │   │   ├── page.tsx             # Dashboard / landing
│   │   │   ├── connections/page.tsx # DB connection management
│   │   │   ├── query/page.tsx       # Chat-based query interface
│   │   │   └── history/page.tsx     # Query history viewer
│   │   ├── components/
│   │   │   ├── DataTable.tsx    # Sortable data table
│   │   │   ├── ChartView.tsx    # Bar/Line/Pie chart component
│   │   │   └── AiInsights.tsx   # AI summary & insights card
│   │   └── lib/
│   │       └── api.ts           # Axios API client
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── .gitignore
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env and set:
#   GROQ_API_KEY=your_groq_api_key
#   ENCRYPTION_KEY=<run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# Run the server
uvicorn app.main:app --reload --port 8000
```

Backend API docs at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

Frontend at: `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/organizations/` | Create organization |
| GET | `/api/organizations/` | List organizations |
| POST | `/api/organizations/{id}/users` | Create user |
| POST | `/api/connections/test` | Test DB connection |
| POST | `/api/connections/` | Save DB connection |
| GET | `/api/connections/org/{org_id}` | List connections |
| GET | `/api/connections/{id}/schema` | Get DB schema |
| POST | `/api/query/` | Run NL query |
| POST | `/api/query/download` | Download report |
| GET | `/api/query/history/{user_id}` | Query history |

## Workflow

1. **Create Organization** → get `org_id`
2. **Create User** → get `user_id`
3. **Add Database Connection** → provide read-only credentials → get `connection_id`
4. **Ask Questions** → type natural language → AI generates SQL → executes → returns results + insights
5. **Download Reports** → CSV, Excel, JSON, or PDF

## Security

- **Read-only access**: Only `SELECT` and `WITH` queries allowed
- **SQL validation**: Blocks `DELETE`, `UPDATE`, `INSERT`, `DROP`, `ALTER`, and 10+ dangerous commands
- **Encrypted credentials**: Database passwords encrypted with Fernet (AES-128-CBC)
- **Query limits**: Max 1000 rows, 10-second timeout
- **Multi-statement blocking**: Prevents SQL injection via semicolons
- **Comment stripping**: Blocks `--` and `/* */` in queries

## Deployment

- **Frontend**: Deploy to Vercel (`vercel --prod` from `/frontend`)
- **Backend**: Deploy to Render (Docker, using `/backend/Dockerfile`)
- **AI**: Uses Groq API (get key at https://console.groq.com)

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 14, React 18, Tailwind CSS, Chart.js |
| Backend | FastAPI, Python 3.11, SQLAlchemy, Pandas, NumPy |
| AI | Groq API (Llama 3.1 70B) |
| Security | Fernet/AES encryption, SQL validation |
| Reports | ReportLab (PDF), openpyxl (Excel), Pandas (CSV) |
| Deploy | Vercel (FE), Render (BE), Docker |
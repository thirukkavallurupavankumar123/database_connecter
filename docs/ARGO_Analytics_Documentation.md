# ARGO Analytics Platform
## Complete Technical Documentation

**Version:** 1.0.0  
**Date:** March 8, 2026  
**Platform:** AI-Powered Natural Language Database Analytics

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [User Access Workflow](#4-user-access-workflow)
5. [Component Architecture](#5-component-architecture)
6. [File Structure & Connections](#6-file-structure--connections)
7. [Database Schema](#7-database-schema)
8. [API Endpoints Reference](#8-api-endpoints-reference)
9. [Data Flow Diagrams](#9-data-flow-diagrams)
10. [Security Architecture](#10-security-architecture)
11. [Deployment Guide](#11-deployment-guide)

---

## 1. Executive Summary

ARGO Analytics is an AI-powered database analytics platform that enables users to query databases using natural language. The system translates human questions into SQL queries, executes them against connected databases, and returns structured results with AI-generated insights.

### Key Features
- **Natural Language to SQL**: Ask questions in plain English
- **Multi-Database Support**: PostgreSQL, MySQL, SQL Server, Snowflake, BigQuery
- **Multi-Tenant Architecture**: Organization-based isolation
- **AI-Powered Insights**: Automatic data analysis and trend detection
- **Export Capabilities**: CSV, Excel, JSON, PDF reports
- **Secure Connections**: AES-256 encrypted credentials

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARGO ANALYTICS PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────┐         ┌───────────────┐  │
│  │                 │         │                 │         │               │  │
│  │   FRONTEND      │  HTTP   │    BACKEND      │  SQL    │   CLIENT      │  │
│  │   Next.js       │◄───────►│    FastAPI      │◄───────►│   DATABASES   │  │
│  │   Port: 3000    │  JSON   │    Port: 8000   │         │   (User Data) │  │
│  │                 │         │                 │         │               │  │
│  └─────────────────┘         └────────┬────────┘         └───────────────┘  │
│                                       │                                      │
│                                       │ SQL                                  │
│                                       ▼                                      │
│                              ┌─────────────────┐                             │
│                              │   APP DATABASE  │                             │
│                              │   PostgreSQL    │                             │
│                              │   (Render.com)  │                             │
│                              │   - Users       │                             │
│                              │   - Orgs        │                             │
│                              │   - Connections │                             │
│                              │   - History     │                             │
│                              └─────────────────┘                             │
│                                                                              │
│                              ┌─────────────────┐                             │
│                              │   GROQ LLM API  │                             │
│                              │   Llama 3.3 70B │                             │
│                              │   (SQL Gen)     │                             │
│                              └─────────────────┘                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 14, React, TypeScript | User interface, dashboard |
| Backend | FastAPI, Python 3.12 | REST API, business logic |
| App Database | PostgreSQL (Render) | User data, connections, history |
| AI Engine | Groq API (Llama 3.3 70B) | Natural language to SQL |
| Client DBs | MySQL, PostgreSQL, etc. | User's data sources |

---

## 3. Technology Stack

### Backend Stack
```
┌─────────────────────────────────────────────┐
│              BACKEND (Python)               │
├─────────────────────────────────────────────┤
│  Framework:     FastAPI 0.109+              │
│  Server:        Uvicorn (ASGI)              │
│  ORM:           SQLAlchemy 2.0              │
│  Migrations:    Alembic                     │
│  Auth:          bcrypt + JWT-like sessions  │
│  Encryption:    cryptography (Fernet)       │
│  AI:            Groq API (groq-python)      │
│  DB Drivers:    psycopg2, pymysql, pyodbc   │
└─────────────────────────────────────────────┘
```

### Frontend Stack
```
┌─────────────────────────────────────────────┐
│             FRONTEND (TypeScript)           │
├─────────────────────────────────────────────┤
│  Framework:     Next.js 14                  │
│  Language:      TypeScript                  │
│  Styling:       Tailwind CSS                │
│  Charts:        Recharts                    │
│  HTTP Client:   Fetch API                   │
│  State:         React Context               │
└─────────────────────────────────────────────┘
```

---

## 4. User Access Workflow

### 4.1 Complete User Journey Flowchart

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         USER ACCESS WORKFLOW                                  │
└──────────────────────────────────────────────────────────────────────────────┘

       START
         │
         ▼
    ┌─────────┐      No     ┌─────────────┐
    │ Account │───────────►│   SIGNUP    │
    │ Exists? │             │   Flow      │
    └────┬────┘             └──────┬──────┘
         │ Yes                     │
         ▼                         │
    ┌─────────┐                    │
    │  LOGIN  │◄───────────────────┘
    │  Page   │
    └────┬────┘
         │
         ▼
    ┌──────────────┐
    │ Auth Check   │
    │ (API Call)   │
    └──────┬───────┘
           │
      ┌────┴────┐
      │ Valid?  │
      └────┬────┘
           │
     ┌─────┴─────┐
    No           Yes
     │            │
     ▼            ▼
  ┌──────┐   ┌───────────────┐
  │Error │   │   DASHBOARD   │
  │ Msg  │   │   (Home)      │
  └──────┘   └───────┬───────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ MANAGE  │ │  QUERY  │ │ HISTORY │
    │ CONNEC. │ │  PAGE   │ │  PAGE   │
    └────┬────┘ └────┬────┘ └─────────┘
         │           │
         ▼           ▼
    ┌─────────┐ ┌─────────────────┐
    │   ADD   │ │ SELECT DATABASE │
    │ DATABASE│ │  CONNECTION     │
    └────┬────┘ └────────┬────────┘
         │               │
         ▼               ▼
    ┌─────────┐ ┌─────────────────┐
    │  TEST   │ │  ENTER NATURAL  │
    │ CONNECT │ │  LANGUAGE QUERY │
    └────┬────┘ └────────┬────────┘
         │               │
         ▼               ▼
    ┌─────────┐ ┌─────────────────┐
    │  SAVE   │ │   AI GENERATES  │
    │ CONFIG  │ │   SQL QUERY     │
    └─────────┘ └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  EXECUTE ON     │
                │  USER DATABASE  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  VIEW RESULTS   │
                │  + AI INSIGHTS  │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │  EXPORT  │          │  SAVE TO │
        │  REPORT  │          │  HISTORY │
        └──────────┘          └──────────┘
```

### 4.2 Signup Flow

```
┌────────────────────────────────────────────────────────────┐
│                    SIGNUP WORKFLOW                          │
└────────────────────────────────────────────────────────────┘

  User                   Frontend                    Backend
    │                       │                           │
    │──── Enter Details ───►│                           │
    │     - Email           │                           │
    │     - Password        │                           │
    │     - Name            │                           │
    │     - Org Name        │                           │
    │     - Org Password    │                           │
    │                       │                           │
    │                       │── POST /api/auth/signup ─►│
    │                       │                           │
    │                       │                    ┌──────┴──────┐
    │                       │                    │ Check Org   │
    │                       │                    │ Exists?     │
    │                       │                    └──────┬──────┘
    │                       │                           │
    │                       │             ┌─────────────┼────────────┐
    │                       │             │             │            │
    │                       │            New        Existing      Wrong
    │                       │            Org        Org+Pass      Pass
    │                       │             │             │            │
    │                       │             ▼             ▼            ▼
    │                       │         Create        Add User      Error
    │                       │         Org+User      to Org        403
    │                       │             │             │            │
    │                       │◄────────────┴─────────────┴────────────┘
    │                       │                           │
    │◄──── Response ────────│                           │
    │    (user_id, org_id)  │                           │
```

### 4.3 Query Execution Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       QUERY EXECUTION PIPELINE                              │
└────────────────────────────────────────────────────────────────────────────┘

  1. INPUT           2. PROCESS           3. AI              4. EXECUTE           5. OUTPUT
  ──────────────────────────────────────────────────────────────────────────────────────────
                                                                                   
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │ Natural     │   │ Load Schema │   │ Groq LLM    │   │ Execute     │   │ Return      │
  │ Language    │──►│ Context     │──►│ Generate    │──►│ SQL Query   │──►│ Results     │
  │ Query       │   │ from Cache  │   │ SQL         │   │ Read-Only   │   │ + Insights  │
  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
        │                 │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼                 ▼
  "Show top 10      Tables:              SELECT name,        ┌─────────┐      {
   customers"       - customers          city FROM            │ MySQL   │        sql: "...",
                    - orders             customers            │ Server  │        data: [...],
                    - products           LIMIT 10             └─────────┘        insights: {...}
                                                                               }
```

---

## 5. Component Architecture

### 5.1 Backend Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐     │
│    │                         main.py                                   │     │
│    │                    (FastAPI Application)                          │     │
│    │   - CORS middleware                                               │     │
│    │   - Router registration                                           │     │
│    │   - Health endpoints                                              │     │
│    └────────────────────────────┬─────────────────────────────────────┘     │
│                                 │                                            │
│           ┌─────────────────────┼─────────────────────┐                     │
│           │                     │                     │                     │
│           ▼                     ▼                     ▼                     │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐               │
│    │  api/       │      │  models/    │      │  services/  │               │
│    │  (Routers)  │      │  (ORM)      │      │  (Logic)    │               │
│    └──────┬──────┘      └──────┬──────┘      └──────┬──────┘               │
│           │                    │                    │                       │
│    ┌──────┴──────┐      ┌──────┴──────┐     ┌──────┴───────────────────┐   │
│    │auth.py      │      │models.py    │     │database_connector.py    │   │
│    │connections  │      │- Organization│     │schema_extractor.py     │   │
│    │organizations│      │- User        │     │query_executor.py       │   │
│    │queries.py   │      │- Connection  │     │sql_validator.py        │   │
│    └─────────────┘      │- QueryHistory│     │encryption.py           │   │
│                         │- SchemaCache │     │data_processor.py       │   │
│                         └──────────────┘     │report_generator.py     │   │
│                                              └─────────────────────────┘   │
│                                                                              │
│    ┌───────────────────────────────────────────────────────────────────┐    │
│    │                        agents/                                     │    │
│    │  ┌─────────────────────┐  ┌─────────────────────────┐             │    │
│    │  │  query_agent.py     │  │  analysis_agent.py      │             │    │
│    │  │  - generate_sql()   │  │  - analyze_data()       │             │    │
│    │  │  - Groq API calls   │  │  - AI insights          │             │    │
│    │  └─────────────────────┘  └─────────────────────────┘             │    │
│    └───────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Frontend Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐     │
│    │                      src/app/layout.tsx                           │     │
│    │                    (Root Layout + AppShell)                       │     │
│    └────────────────────────────┬─────────────────────────────────────┘     │
│                                 │                                            │
│           ┌─────────────────────┼─────────────────────┐                     │
│           │                     │                     │                     │
│           ▼                     ▼                     ▼                     │
│    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐               │
│    │   /login    │      │   /query    │      │ /connections│               │
│    │   page.tsx  │      │   page.tsx  │      │   page.tsx  │               │
│    └──────┬──────┘      └──────┬──────┘      └──────┬──────┘               │
│           │                    │                    │                       │
│           │             ┌──────┴──────┐            │                       │
│           │             │             │            │                       │
│           ▼             ▼             ▼            ▼                       │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                       components/                                │     │
│    │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐│     │
│    │  │ AppShell  │ │ DataTable │ │ ChartView │ │ AiInsights        ││     │
│    │  │ (Nav/Side)│ │ (Results) │ │ (Recharts)│ │ (AI Analysis)     ││     │
│    │  └───────────┘ └───────────┘ └───────────┘ └───────────────────┘│     │
│    │  ┌───────────┐                                                   │     │
│    │  │ AuthGuard │                                                   │     │
│    │  │ (Session) │                                                   │     │
│    │  └───────────┘                                                   │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                         lib/                                     │     │
│    │  ┌─────────────────────────────────────────────────────────────┐│     │
│    │  │  api.ts - API client functions                              ││     │
│    │  │  - login(), signup()                                        ││     │
│    │  │  - testConnection(), saveConnection()                       ││     │
│    │  │  - executeQuery(), exportReport()                           ││     │
│    │  └─────────────────────────────────────────────────────────────┘│     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. File Structure & Connections

### 6.1 Complete Project Structure

```
ARGO_project/
│
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # ← FastAPI app entry point
│   │   ├── config.py                 # ← Settings & environment variables
│   │   ├── database.py               # ← SQLAlchemy engine & session
│   │   │
│   │   ├── api/                      # ← API Route Handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # POST /api/auth/signup, /login
│   │   │   ├── connections.py        # CRUD /api/connections/*
│   │   │   ├── organizations.py      # CRUD /api/orgs/*
│   │   │   └── queries.py            # POST /api/query/*
│   │   │
│   │   ├── models/                   # ← SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   └── models.py             # Organization, User, Connection, etc.
│   │   │
│   │   ├── schemas/                  # ← Pydantic Request/Response Models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # QueryRequest, QueryResponse, etc.
│   │   │
│   │   ├── services/                 # ← Business Logic Services
│   │   │   ├── database_connector.py # Build connection URLs
│   │   │   ├── schema_extractor.py   # Extract table schemas
│   │   │   ├── query_executor.py     # Execute SQL safely
│   │   │   ├── sql_validator.py      # Validate SQL syntax
│   │   │   ├── encryption.py         # AES encrypt/decrypt
│   │   │   ├── data_processor.py     # Statistics & trends
│   │   │   └── report_generator.py   # CSV, Excel, PDF export
│   │   │
│   │   └── agents/                   # ← AI Agents
│   │       ├── query_agent.py        # NL → SQL using Groq LLM
│   │       └── analysis_agent.py     # Data analysis insights
│   │
│   ├── alembic/                      # ← Database migrations
│   │   ├── versions/                 # Migration scripts
│   │   └── env.py
│   │
│   ├── .env                          # Environment variables
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Docker build
│
├── frontend/                         # Next.js Frontend
│   ├── src/
│   │   ├── app/                      # ← Next.js App Router Pages
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Home redirect
│   │   │   ├── login/page.tsx        # Login/Signup page
│   │   │   ├── query/page.tsx        # Main query interface
│   │   │   ├── connections/page.tsx  # Manage connections
│   │   │   └── history/page.tsx      # Query history
│   │   │
│   │   ├── components/               # ← Reusable UI Components
│   │   │   ├── AppShell.tsx          # Navigation shell
│   │   │   ├── AuthGuard.tsx         # Auth wrapper
│   │   │   ├── DataTable.tsx         # Results table
│   │   │   ├── ChartView.tsx         # Data visualization
│   │   │   └── AiInsights.tsx        # AI insights panel
│   │   │
│   │   └── lib/                      # ← Utilities
│   │       └── api.ts                # API client functions
│   │
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml                # Local development
├── render.yaml                       # Render.com deployment
└── README.md
```

### 6.2 File Connection Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FILE DEPENDENCY CONNECTIONS                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌───────────────┐
                              │   main.py     │
                              │  (Entry Point)│
                              └───────┬───────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
       ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
       │  config.py  │         │ database.py │         │ api/*.py    │
       │  (Settings) │◄────────│ (Engine)    │         │ (Routers)   │
       └─────────────┘         └──────┬──────┘         └──────┬──────┘
                                      │                       │
                                      │               ┌───────┴───────┐
                                      │               │               │
                                      ▼               ▼               ▼
                               ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
                               │ models.py   │ │ schemas.py  │ │ services/*  │
                               │ (ORM)       │ │ (Pydantic)  │ │ (Logic)     │
                               └─────────────┘ └─────────────┘ └──────┬──────┘
                                                                      │
                                                              ┌───────┴───────┐
                                                              │               │
                                                              ▼               ▼
                                                       ┌─────────────┐ ┌─────────────┐
                                                       │ agents/*    │ │ encryption  │
                                                       │ (AI/LLM)    │ │ (Fernet)    │
                                                       └─────────────┘ └─────────────┘
```

### 6.3 API Router to Service Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ROUTER → SERVICE DEPENDENCIES                          │
└─────────────────────────────────────────────────────────────────────────────┘

  api/auth.py
      │
      └──► models.py (User, Organization)
      └──► encryption.py (password hashing - bcrypt)

  api/connections.py
      │
      └──► models.py (DatabaseConnection, SchemaCache)
      └──► database_connector.py (build URLs, test connections)
      └──► schema_extractor.py (extract table/column metadata)
      └──► encryption.py (encrypt/decrypt passwords)

  api/queries.py
      │
      └──► models.py (QueryHistory, User, Connection)
      └──► database_connector.py (get client engine)
      └──► schema_extractor.py (context for AI)
      └──► agents/query_agent.py (NL → SQL)
      └──► sql_validator.py (safety checks)
      └──► query_executor.py (run SQL)
      └──► agents/analysis_agent.py (AI insights)
      └──► data_processor.py (statistics)
      └──► report_generator.py (export)

  api/organizations.py
      │
      └──► models.py (Organization)
```

---

## 7. Database Schema

### 7.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION DATABASE SCHEMA (ERD)                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────────────────┐
  │                            ORGANIZATIONS                                   │
  ├───────────────────────────────────────────────────────────────────────────┤
  │  id (PK)           │ VARCHAR   │ UUID primary key                         │
  │  name              │ VARCHAR   │ Organization name                        │
  │  password_hash     │ VARCHAR   │ bcrypt hashed password                   │
  │  created_at        │ TIMESTAMP │ Creation timestamp                       │
  └───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1:N
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 │
  ┌─────────────────────────────┐   ┌─────────────────────────────┐
  │           USERS             │   │    DATABASE_CONNECTIONS     │
  ├─────────────────────────────┤   ├─────────────────────────────┤
  │  id (PK)         │ VARCHAR  │   │  id (PK)         │ VARCHAR  │
  │  email           │ VARCHAR  │   │  organization_id │ FK       │
  │  name            │ VARCHAR  │   │  name            │ VARCHAR  │
  │  password_hash   │ VARCHAR  │   │  db_type         │ VARCHAR  │
  │  organization_id │ FK       │   │  host            │ VARCHAR  │
  │  is_active       │ BOOLEAN  │   │  port            │ VARCHAR  │
  │  created_at      │ TIMESTAMP│   │  database_name   │ VARCHAR  │
  └─────────────────────────────┘   │  username        │ VARCHAR  │
              │                      │  encrypted_pass  │ TEXT     │
              │ 1:N                  │  ssl_enabled     │ BOOLEAN  │
              ▼                      │  is_active       │ BOOLEAN  │
  ┌─────────────────────────────┐   │  created_at      │ TIMESTAMP│
  │       QUERY_HISTORY         │   │  last_used_at    │ TIMESTAMP│
  ├─────────────────────────────┤   └─────────────────────────────┘
  │  id (PK)         │ VARCHAR  │               │
  │  user_id (FK)    │ VARCHAR  │               │ 1:1
  │  connection_id   │ FK       │               ▼
  │  natural_lang_q  │ TEXT     │   ┌─────────────────────────────┐
  │  generated_sql   │ TEXT     │   │       SCHEMA_CACHE          │
  │  status          │ VARCHAR  │   ├─────────────────────────────┤
  │  error_message   │ TEXT     │   │  id (PK)         │ VARCHAR  │
  │  row_count       │ VARCHAR  │   │  connection_id   │ FK       │
  │  created_at      │ TIMESTAMP│   │  schema_json     │ TEXT     │
  └─────────────────────────────┘   │  updated_at      │ TIMESTAMP│
                                    └─────────────────────────────┘
```

### 7.2 Table Descriptions

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **organizations** | Multi-tenant isolation | name, password_hash |
| **users** | User accounts within orgs | email, organization_id |
| **database_connections** | Saved DB configs | db_type, host, encrypted_password |
| **schema_cache** | Cached table metadata | schema_json (for AI context) |
| **query_history** | Audit trail | natural_language_query, generated_sql |

---

## 8. API Endpoints Reference

### 8.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user (+ create/join org) |
| POST | `/api/auth/login` | Authenticate user |

### 8.2 Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/connections/test` | Test database connection |
| POST | `/api/connections/` | Save new connection |
| GET | `/api/connections/org/{org_id}` | List org connections |
| GET | `/api/connections/{id}/schema` | Extract & cache schema |
| DELETE | `/api/connections/{id}` | Delete connection |

### 8.3 Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query/` | Execute NL query pipeline |
| POST | `/api/query/export` | Export results (CSV/Excel/PDF) |
| GET | `/api/query/history` | Get user query history |

### 8.4 API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API REQUEST FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  Client Request                                                    Response
       │                                                                │
       │  POST /api/query/                                             │
       │  {                                                            │
       │    "user_id": "abc...",                                       │
       │    "connection_id": "xyz...",                                 │
       │    "natural_language_query": "Show top customers"            │
       │  }                                                            │
       │                                                                │
       ▼                                                                │
  ┌─────────────────┐                                                  │
  │ 1. Validate     │                                                  │
  │    User/Conn    │                                                  │
  └────────┬────────┘                                                  │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐                                                  │
  │ 2. Load Schema  │                                                  │
  │    Context      │                                                  │
  └────────┬────────┘                                                  │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐     ┌──────────────┐                             │
  │ 3. Call Groq    │────►│ Groq API     │                             │
  │    LLM API      │◄────│ Llama 3.3    │                             │
  └────────┬────────┘     └──────────────┘                             │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐                                                  │
  │ 4. Validate     │                                                  │
  │    SQL Safety   │                                                  │
  └────────┬────────┘                                                  │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐     ┌──────────────┐                             │
  │ 5. Execute      │────►│ Client DB    │                             │
  │    Read-Only    │◄────│ (MySQL etc)  │                             │
  └────────┬────────┘     └──────────────┘                             │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐                                                  │
  │ 6. AI Analysis  │                                                  │
  │    & Statistics │                                                  │
  └────────┬────────┘                                                  │
           │                                                            │
           ▼                                                            │
  ┌─────────────────┐                                                  │
  │ 7. Save to      │                                                  │
  │    History      │                                                  │
  └────────┬────────┘                                                  │
           │                                                            │
           └───────────────────────────────────────────────────────────►│
                                                                        │
                                               {                        │
                                                 "sql": "SELECT ...",   │
                                                 "columns": [...],      │
                                                 "data": [...],         │
                                                 "row_count": 10,       │
                                                 "insights": {...}      │
                                               }                        │
```

---

## 9. Data Flow Diagrams

### 9.1 Complete System Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE SYSTEM DATA FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌────────────────┐
                                    │     USER       │
                                    │   (Browser)    │
                                    └───────┬────────┘
                                            │
                                            │ HTTPS
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Login     │  │ Connections │  │   Query     │  │  History    │       │
│  │   Page      │  │   Page      │  │   Page      │  │   Page      │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         └─────────────────┴────────────────┴─────────────────┘             │
│                                    │                                        │
│                           lib/api.ts (HTTP Client)                          │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     │ REST API (JSON)
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                              │
│                                                                              │
│    ┌────────────────────────────────────────────────────────────────────┐   │
│    │                         API LAYER                                   │   │
│    │  /api/auth  │  /api/connections  │  /api/query  │  /api/orgs      │   │
│    └─────────────────────────────┬───────────────────────────────────────┘   │
│                                  │                                           │
│    ┌─────────────────────────────┴───────────────────────────────────────┐   │
│    │                       SERVICE LAYER                                  │   │
│    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│    │  │ Encryption   │  │ DB Connector │  │ Schema       │               │   │
│    │  │ Service      │  │ Service      │  │ Extractor    │               │   │
│    │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│    │  │ SQL          │  │ Query        │  │ Report       │               │   │
│    │  │ Validator    │  │ Executor     │  │ Generator    │               │   │
│    │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│    └──────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│    ┌─────────────────────────────┴───────────────────────────────────────┐   │
│    │                         AI LAYER                                     │   │
│    │  ┌────────────────────────┐  ┌────────────────────────┐             │   │
│    │  │    Query Agent         │  │    Analysis Agent      │             │   │
│    │  │    (NL → SQL)          │  │    (Data → Insights)   │             │   │
│    │  └───────────┬────────────┘  └────────────────────────┘             │   │
│    └──────────────┼───────────────────────────────────────────────────────┘   │
│                   │                                                          │
└───────────────────┼──────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  GROQ API     │       │  APP DATABASE │
│  (Llama 3.3)  │       │  (PostgreSQL) │
│               │       │  - Render.com │
│  NL → SQL     │       │  - Users      │
│  translation  │       │  - Orgs       │
└───────────────┘       │  - Conns      │
                        │  - History    │
                        └───────────────┘
                                │
                                │ (decrypted creds)
                                ▼
                        ┌───────────────┐
                        │ CLIENT DBs    │
                        │ ─────────────│
                        │ • MySQL       │
                        │ • PostgreSQL  │
                        │ • SQL Server  │
                        │ • Snowflake   │
                        │ • BigQuery    │
                        └───────────────┘
```

### 9.2 Query Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      QUERY PROCESSING PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘

 Step 1          Step 2          Step 3          Step 4          Step 5
 ─────────────────────────────────────────────────────────────────────────────
 
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│  INPUT    │   │  CONTEXT  │   │  AI GEN   │   │  VALIDATE │   │  EXECUTE  │
│           │   │  BUILD    │   │           │   │           │   │           │
│ "Show me  │──►│ Load      │──►│ Call Groq │──►│ Check SQL │──►│ Run on    │
│  the top  │   │ schema    │   │ API with  │   │ syntax &  │   │ client    │
│  sellers" │   │ cache for │   │ schema +  │   │ safety    │   │ database  │
│           │   │ tables/   │   │ query     │   │ rules     │   │ (readonly)│
│           │   │ columns   │   │           │   │           │   │           │
└───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘
                     │               │               │               │
                     ▼               ▼               ▼               ▼
              ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
              │ Tables:   │   │ SELECT    │   │ ✓ No DROP │   │ [{...},   │
              │ -products │   │ p.name,   │   │ ✓ No DEL  │   │  {...}]   │
              │ -sales    │   │ SUM(qty)  │   │ ✓ No UPD  │   │  (rows)   │
              │ -customers│   │ FROM ...  │   │ ✓ Valid   │   │           │
              └───────────┘   └───────────┘   └───────────┘   └───────────┘


 Step 6          Step 7          Step 8
 ───────────────────────────────────────────
 
┌───────────┐   ┌───────────┐   ┌───────────┐
│  ANALYZE  │   │  HISTORY  │   │  RESPOND  │
│           │   │           │   │           │
│ AI insight│──►│ Save to   │──►│ Return    │
│ generation│   │ query_    │   │ JSON with │
│ stats &   │   │ history   │   │ all data  │
│ trends    │   │ table     │   │           │
│           │   │           │   │           │
└───────────┘   └───────────┘   └───────────┘
      │               │               │
      ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│ "Product  │   │ Record:   │   │ {         │
│  A shows  │   │ user_id   │   │  sql,     │
│  15%      │   │ query     │   │  data,    │
│  growth"  │   │ sql,time  │   │  insights │
└───────────┘   └───────────┘   │ }         │
                                └───────────┘
```

---

## 10. Security Architecture

### 10.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Layer 1: Transport Security
  ───────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  HTTPS/TLS encryption for all client-server communication               │
  │  SSL/TLS for database connections (configurable)                        │
  └─────────────────────────────────────────────────────────────────────────┘

  Layer 2: Authentication
  ───────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  User passwords: bcrypt hashed (work factor 12)                          │
  │  Organization passwords: bcrypt hashed                                   │
  │  Session: User ID + Org ID stored in frontend                            │
  └─────────────────────────────────────────────────────────────────────────┘

  Layer 3: Authorization
  ───────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Tenant isolation: Users can only access their organization's data       │
  │  Connection access: Verified user.org_id == connection.org_id           │
  │  Query execution: Only against user's authorized connections             │
  └─────────────────────────────────────────────────────────────────────────┘

  Layer 4: Data Protection
  ───────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Database credentials: AES-256 encrypted (Fernet)                        │
  │  Encryption key: Environment variable (ENCRYPTION_KEY)                   │
  │  Credentials never logged or exposed in responses                        │
  └─────────────────────────────────────────────────────────────────────────┘

  Layer 5: Query Safety
  ───────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  SQL validation: Block DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE    │
  │  Read-only execution: Only SELECT statements allowed                     │
  │  AI-generated SQL: Validated before execution                            │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Credential Flow

```
  User enters DB password
          │
          ▼
  ┌───────────────┐
  │ Frontend form │
  │ (plain text)  │
  └───────┬───────┘
          │ HTTPS POST
          ▼
  ┌───────────────┐     ┌───────────────┐
  │ Backend API   │────►│ Fernet.       │
  │ connections.py│     │ encrypt()     │
  └───────────────┘     └───────┬───────┘
                                │
                        ┌───────┴───────┐
                        │ encrypted_    │
                        │ password      │
                        └───────┬───────┘
                                │
                        ┌───────┴───────┐
                        │ Store in      │
                        │ PostgreSQL    │
                        └───────────────┘


  Query Execution (retrieval):
  
  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
  │ Load from DB  │────►│ Fernet.       │────►│ Build conn    │
  │ (encrypted)   │     │ decrypt()     │     │ URL, execute  │
  └───────────────┘     └───────────────┘     └───────────────┘
```

---

## 11. Deployment Guide

### 11.1 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PRODUCTION DEPLOYMENT (Render.com)                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                            Render.com                                    │
  │  ┌────────────────────────────────────────────────────────────────────┐ │
  │  │                        Web Services                                 │ │
  │  │  ┌─────────────────┐              ┌─────────────────┐              │ │
  │  │  │   Backend       │              │   Frontend      │              │ │
  │  │  │   (FastAPI)     │              │   (Next.js)     │              │ │
  │  │  │                 │              │                 │              │ │
  │  │  │ argo-backend    │◄────────────►│ argo-frontend   │              │ │
  │  │  │ .onrender.com   │   Internal   │ .onrender.com   │              │ │
  │  │  │                 │   Network    │                 │              │ │
  │  │  └────────┬────────┘              └─────────────────┘              │ │
  │  │           │                                                         │ │
  │  │           │ Internal connection (Render private network)            │ │
  │  │           ▼                                                         │ │
  │  │  ┌─────────────────┐                                               │ │
  │  │  │   PostgreSQL    │                                               │ │
  │  │  │   Database      │                                               │ │
  │  │  │                 │                                               │ │
  │  │  │ dataanalys DB   │                                               │ │
  │  │  │ Oregon region   │                                               │ │
  │  │  └─────────────────┘                                               │ │
  │  └────────────────────────────────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ External HTTPS
                                     ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          External Services                               │
  │  ┌─────────────────┐              ┌─────────────────┐                   │
  │  │   Groq API      │              │   User's DBs    │                   │
  │  │   (AI/LLM)      │              │   (MySQL, etc)  │                   │
  │  └─────────────────┘              └─────────────────┘                   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Backend | Fernet key for credential encryption |
| `GROQ_API_KEY` | Backend | Groq API key for LLM access |
| `FRONTEND_URL` | Backend | Frontend URL for CORS |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API URL |

### 11.3 Local Development Setup

```bash
# 1. Clone repository
git clone <repository>
cd ARGO_project

# 2. Setup Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Set environment variables
$env:DATABASE_URL = "postgresql://..."
$env:ENCRYPTION_KEY = "your-key"
$env:GROQ_API_KEY = "your-groq-key"

# 5. Run migrations
alembic upgrade head

# 6. Start backend
uvicorn app.main:app --reload --port 8000

# 7. In new terminal - setup frontend
cd frontend
npm install
npm run dev
```

---

## Summary

ARGO Analytics provides a complete AI-powered database analytics solution with:

- **Secure multi-tenant architecture** with organization-based isolation
- **Natural language interface** powered by Groq Llama 3.3 70B
- **Multi-database support** for major database platforms
- **End-to-end encryption** for stored credentials
- **Comprehensive audit trail** of all queries
- **Export capabilities** for reporting needs

The modular architecture allows easy extension and maintenance, while the clear separation of concerns ensures security and scalability.

---

*Document generated for ARGO Analytics Platform v1.0.0*

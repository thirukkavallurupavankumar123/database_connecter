"""
ARGO Analytics Platform - PDF Documentation Generator
Generates comprehensive PDF documentation with flowcharts and architecture diagrams
"""
from fpdf import FPDF
from pathlib import Path
from datetime import datetime


class ARGODocPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'ARGO Analytics Platform - Technical Documentation', align='C')
            self.ln(8)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def title_page(self):
        self.add_page()
        self.ln(60)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(26, 54, 93)
        self.cell(0, 15, 'ARGO Analytics Platform', align='C', ln=True)
        self.ln(5)
        self.set_font('Helvetica', '', 18)
        self.set_text_color(74, 85, 104)
        self.cell(0, 10, 'Complete Technical Documentation', align='C', ln=True)
        self.ln(20)
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'AI-Powered Natural Language Database Analytics', align='C', ln=True)
        self.ln(40)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, f'Version: 1.0.0', align='C', ln=True)
        self.cell(0, 8, f'Date: {datetime.now().strftime("%B %d, %Y")}', align='C', ln=True)
    
    def chapter_title(self, num, title):
        self.add_page()
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(43, 108, 176)
        self.cell(0, 12, f'{num}. {title}', ln=True)
        self.set_draw_color(190, 227, 248)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)
    
    def section_title(self, title):
        self.ln(5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(44, 82, 130)
        self.cell(0, 10, title, ln=True)
        self.ln(2)
    
    def subsection_title(self, title):
        self.ln(3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(45, 55, 72)
        self.cell(0, 8, title, ln=True)
        self.ln(1)
    
    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        self.multi_cell(0, 6, text)
        self.ln(2)
    
    def bullet_list(self, items):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        for item in items:
            self.cell(8, 6, chr(149))
            self.multi_cell(180, 6, item)
            self.ln(1)
    
    def code_block(self, code, font_size=7):
        self.set_font('Courier', '', font_size)
        self.set_fill_color(26, 32, 44)
        self.set_text_color(226, 232, 240)
        lines = code.strip().split('\n')
        for line in lines:
            self.cell(0, 4.5, '  ' + line, fill=True, ln=True)
        self.ln(3)
        self.set_text_color(51, 51, 51)
    
    def add_table(self, headers, rows, col_widths=None):
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(43, 108, 176)
        self.set_text_color(255, 255, 255)
        
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(51, 51, 51)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(247, 250, 252)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)


def generate_documentation():
    pdf = ARGODocPDF()
    
    # Title Page
    pdf.title_page()
    
    # Table of Contents
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 12, 'Table of Contents', ln=True)
    pdf.ln(5)
    
    toc_items = [
        ('1', 'Executive Summary', 3),
        ('2', 'System Architecture Overview', 4),
        ('3', 'Technology Stack', 5),
        ('4', 'User Access Workflow', 6),
        ('5', 'Component Architecture', 8),
        ('6', 'File Structure & Connections', 10),
        ('7', 'Database Schema', 12),
        ('8', 'API Endpoints Reference', 13),
        ('9', 'Data Flow Diagrams', 14),
        ('10', 'Security Architecture', 16),
        ('11', 'Deployment Guide', 17),
    ]
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(51, 51, 51)
    for num, title, page in toc_items:
        pdf.cell(15, 8, num)
        pdf.cell(150, 8, title)
        pdf.cell(0, 8, str(page), align='R', ln=True)
    
    # Chapter 1: Executive Summary
    pdf.chapter_title('1', 'Executive Summary')
    pdf.body_text(
        'ARGO Analytics is an AI-powered database analytics platform that enables users to query '
        'databases using natural language. The system translates human questions into SQL queries, '
        'executes them against connected databases, and returns structured results with AI-generated insights.'
    )
    
    pdf.section_title('Key Features')
    pdf.bullet_list([
        'Natural Language to SQL: Ask questions in plain English',
        'Multi-Database Support: PostgreSQL, MySQL, SQL Server, Snowflake, BigQuery',
        'Multi-Tenant Architecture: Organization-based isolation',
        'AI-Powered Insights: Automatic data analysis and trend detection',
        'Export Capabilities: CSV, Excel, JSON, PDF reports',
        'Secure Connections: AES-256 encrypted credentials',
    ])
    
    # Chapter 2: System Architecture
    pdf.chapter_title('2', 'System Architecture Overview')
    pdf.body_text(
        'The ARGO platform follows a three-tier architecture with a Next.js frontend, '
        'FastAPI backend, and PostgreSQL database for application data. Client databases '
        'are queried dynamically based on user connections.'
    )
    
    pdf.section_title('High-Level Architecture Diagram')
    arch_diagram = """
+-----------------------------------------------------------------------------+
|                      ARGO ANALYTICS PLATFORM                                 |
+-----------------------------------------------------------------------------+
|                                                                              |
|  +-----------+         +-----------+         +-----------+                  |
|  |           |  HTTP   |           |  SQL    |  CLIENT   |                  |
|  | FRONTEND  |<------->| BACKEND   |<------->| DATABASES |                  |
|  | Next.js   |  JSON   | FastAPI   |         | (User)    |                  |
|  | Port:3000 |         | Port:8000 |         |           |                  |
|  +-----------+         +-----+-----+         +-----------+                  |
|                              |                                               |
|                              | SQL                                           |
|                              v                                               |
|                        +-----------+        +-----------+                    |
|                        |    APP    |        |  GROQ     |                    |
|                        | DATABASE  |        |  LLM API  |                    |
|                        | PostgreSQL|        | Llama 3.3 |                    |
|                        +-----------+        +-----------+                    |
+-----------------------------------------------------------------------------+
"""
    pdf.code_block(arch_diagram, 6)
    
    pdf.section_title('Architecture Components')
    pdf.add_table(
        ['Component', 'Technology', 'Purpose'],
        [
            ['Frontend', 'Next.js 14, React, TypeScript', 'User interface, dashboard'],
            ['Backend', 'FastAPI, Python 3.12', 'REST API, business logic'],
            ['App Database', 'PostgreSQL (Render)', 'User data, connections, history'],
            ['AI Engine', 'Groq API (Llama 3.3 70B)', 'Natural language to SQL'],
            ['Client DBs', 'MySQL, PostgreSQL, etc.', "User's data sources"],
        ],
        [35, 65, 90]
    )
    
    # Chapter 3: Technology Stack
    pdf.chapter_title('3', 'Technology Stack')
    
    pdf.section_title('Backend Stack')
    pdf.add_table(
        ['Category', 'Technology'],
        [
            ['Framework', 'FastAPI 0.109+'],
            ['Server', 'Uvicorn (ASGI)'],
            ['ORM', 'SQLAlchemy 2.0'],
            ['Migrations', 'Alembic'],
            ['Auth', 'bcrypt + session-based'],
            ['Encryption', 'cryptography (Fernet/AES-256)'],
            ['AI', 'Groq API (groq-python)'],
            ['DB Drivers', 'psycopg2, pymysql, pyodbc'],
        ],
        [60, 130]
    )
    
    pdf.section_title('Frontend Stack')
    pdf.add_table(
        ['Category', 'Technology'],
        [
            ['Framework', 'Next.js 14'],
            ['Language', 'TypeScript'],
            ['Styling', 'Tailwind CSS'],
            ['Charts', 'Recharts'],
            ['HTTP Client', 'Fetch API'],
            ['State', 'React Context'],
        ],
        [60, 130]
    )
    
    # Chapter 4: User Access Workflow
    pdf.chapter_title('4', 'User Access Workflow')
    pdf.body_text(
        'This section describes how users interact with the ARGO platform, from initial signup '
        'through querying their databases using natural language.'
    )
    
    pdf.section_title('Complete User Journey Flowchart')
    user_flow = """
                                START
                                  |
                                  v
                            +-----------+
                            | Account   |----No----> SIGNUP FLOW
                            | Exists?   |                |
                            +-----+-----+                |
                                  | Yes                  |
                                  v                      |
                            +-----------+                |
                            |  LOGIN    |<---------------+
                            |  Page     |
                            +-----+-----+
                                  |
                                  v
                            +-----------+
                            | Auth OK?  |----No----> Error Message
                            +-----+-----+
                                  | Yes
                                  v
                            +-----------+
                            | DASHBOARD |
                            +-----+-----+
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
        +-----------+       +-----------+       +-----------+
        | MANAGE    |       |  QUERY    |       | HISTORY   |
        | CONNECTIONS|       |  PAGE     |       | PAGE      |
        +-----------+       +-----+-----+       +-----------+
              |                   |
              v                   v
        +-----------+       +-----------+
        | ADD/TEST  |       | SELECT DB |
        | DATABASE  |       | CONNECTION|
        +-----------+       +-----+-----+
                                  |
                                  v
                            +-----------+
                            | ENTER NL  |
                            | QUERY     |
                            +-----+-----+
                                  |
                                  v
                            +-----------+
                            | AI GENER- |
                            | ATES SQL  |
                            +-----+-----+
                                  |
                                  v
                            +-----------+
                            | EXECUTE & |
                            | RETURN    |
                            +-----------+
"""
    pdf.code_block(user_flow, 5.5)
    
    pdf.section_title('Query Execution Pipeline')
    query_pipeline = """
  INPUT          CONTEXT        AI GEN         VALIDATE       EXECUTE        OUTPUT
    |               |              |              |              |              |
    v               v              v              v              v              v
+--------+     +--------+     +--------+     +--------+     +--------+     +--------+
|Natural |     | Load   |     | Groq   |     | Check  |     | Run on |     | Return |
|Language|---->| Schema |---->| LLM    |---->| SQL    |---->| Client |---->| Data + |
|Query   |     | Cache  |     | API    |     | Safety |     | DB     |     |Insights|
+--------+     +--------+     +--------+     +--------+     +--------+     +--------+

Example:
"Show top 10    Tables:        SELECT name,   No DROP/      MySQL         {sql,
 customers"    -customers      city FROM      DELETE/       Server        data,
               -orders         customers      UPDATE                      insights}
"""
    pdf.code_block(query_pipeline, 6)
    
    # Chapter 5: Component Architecture
    pdf.chapter_title('5', 'Component Architecture')
    
    pdf.section_title('Backend Component Diagram')
    backend_arch = """
+-------------------------------------------------------------------------+
|                         BACKEND ARCHITECTURE                             |
+-------------------------------------------------------------------------+
|                                                                          |
|   +----------------------------------------------------------------+    |
|   |                        main.py                                  |    |
|   |                   (FastAPI Application)                         |    |
|   |   - CORS middleware    - Router registration                    |    |
|   +------------------------------+---------------------------------+    |
|                                  |                                       |
|          +-----------------------+-----------------------+               |
|          |                       |                       |               |
|          v                       v                       v               |
|   +------------+          +------------+          +------------+         |
|   |   api/     |          |  models/   |          | services/  |         |
|   |  (Routers) |          |   (ORM)    |          |  (Logic)   |         |
|   +-----+------+          +-----+------+          +-----+------+         |
|         |                       |                       |                |
|   +-----------+           +-----------+          +---------------+       |
|   | auth.py   |           | models.py |          | db_connector  |       |
|   | connections|           | -Org      |          | encryption    |       |
|   | queries   |           | -User     |          | sql_validator |       |
|   | orgs      |           | -Conn     |          | query_executor|       |
|   +-----------+           +-----------+          +---------------+       |
|                                                                          |
|   +----------------------------------------------------------------+    |
|   |                         agents/                                 |    |
|   |   +-----------------------+   +------------------------+       |    |
|   |   | query_agent.py        |   | analysis_agent.py      |       |    |
|   |   | (NL to SQL via Groq)  |   | (Data to Insights)     |       |    |
|   |   +-----------------------+   +------------------------+       |    |
|   +----------------------------------------------------------------+    |
+-------------------------------------------------------------------------+
"""
    pdf.code_block(backend_arch, 5.5)
    
    pdf.section_title('Frontend Component Diagram')
    frontend_arch = """
+-------------------------------------------------------------------------+
|                        FRONTEND ARCHITECTURE                             |
+-------------------------------------------------------------------------+
|                                                                          |
|   +----------------------------------------------------------------+    |
|   |                    src/app/layout.tsx                           |    |
|   |                  (Root Layout + AppShell)                       |    |
|   +-----------------------------+----------------------------------+    |
|                                 |                                        |
|         +-----------------------+-----------------------+                |
|         |                       |                       |                |
|         v                       v                       v                |
|   +------------+          +------------+          +------------+         |
|   |  /login    |          |  /query    |          |/connections|         |
|   |  page.tsx  |          |  page.tsx  |          |  page.tsx  |         |
|   +------------+          +------------+          +------------+         |
|                                                                          |
|   +----------------------------------------------------------------+    |
|   |                      components/                                |    |
|   |                                                                  |    |
|   |  AppShell   DataTable   ChartView   AiInsights   AuthGuard     |    |
|   +----------------------------------------------------------------+    |
|                                                                          |
|   +----------------------------------------------------------------+    |
|   |                         lib/                                    |    |
|   |   api.ts - API client functions                                 |    |
|   |   - login(), signup(), testConnection(), executeQuery()        |    |
|   +----------------------------------------------------------------+    |
+-------------------------------------------------------------------------+
"""
    pdf.code_block(frontend_arch, 5.5)
    
    # Chapter 6: File Structure
    pdf.chapter_title('6', 'File Structure & Connections')
    
    pdf.section_title('Complete Project Structure')
    file_structure = """
ARGO_project/
|
+-- backend/                        # Python FastAPI Backend
|   +-- app/
|   |   +-- main.py                 # FastAPI app entry point
|   |   +-- config.py               # Settings & environment variables
|   |   +-- database.py             # SQLAlchemy engine & session
|   |   +-- api/                    # API Route Handlers
|   |   |   +-- auth.py             # POST /api/auth/signup, /login
|   |   |   +-- connections.py      # CRUD /api/connections/*
|   |   |   +-- organizations.py    # CRUD /api/orgs/*
|   |   |   +-- queries.py          # POST /api/query/*
|   |   +-- models/                 # SQLAlchemy ORM Models
|   |   |   +-- models.py           # Organization, User, Connection, etc.
|   |   +-- schemas/                # Pydantic Request/Response Models
|   |   +-- services/               # Business Logic Services
|   |   |   +-- database_connector.py
|   |   |   +-- schema_extractor.py
|   |   |   +-- query_executor.py
|   |   |   +-- encryption.py
|   |   +-- agents/                 # AI Agents
|   |       +-- query_agent.py      # NL to SQL using Groq LLM
|   |       +-- analysis_agent.py   # Data analysis insights
|   +-- alembic/                    # Database migrations
|   +-- requirements.txt
|   +-- Dockerfile
|
+-- frontend/                       # Next.js Frontend
|   +-- src/
|   |   +-- app/                    # Next.js App Router Pages
|   |   |   +-- layout.tsx
|   |   |   +-- login/page.tsx
|   |   |   +-- query/page.tsx
|   |   |   +-- connections/page.tsx
|   |   +-- components/             # Reusable UI Components
|   |   +-- lib/api.ts              # API client functions
|   +-- package.json
|   +-- Dockerfile
|
+-- docker-compose.yml
+-- render.yaml
+-- README.md
"""
    pdf.code_block(file_structure, 5.5)
    
    pdf.section_title('File Dependency Connections')
    file_deps = """
                              +---------------+
                              |   main.py     |
                              | (Entry Point) |
                              +-------+-------+
                                      |
              +-----------------------+-----------------------+
              |                       |                       |
              v                       v                       v
       +------------+          +------------+          +------------+
       | config.py  |          | database.py|          |  api/*.py  |
       | (Settings) |<---------| (Engine)   |          | (Routers)  |
       +------------+          +------+-----+          +------+-----+
                                      |                       |
                                      |               +-------+-------+
                                      |               |       |       |
                                      v               v       v       v
                               +----------+    +--------+ +--------+ +--------+
                               | models.py|    |schemas | |services| | agents |
                               |   (ORM)  |    |        | |        | |  (AI)  |
                               +----------+    +--------+ +--------+ +--------+
"""
    pdf.code_block(file_deps, 6)
    
    # Chapter 7: Database Schema
    pdf.chapter_title('7', 'Database Schema')
    
    pdf.section_title('Entity Relationship Diagram')
    erd = """
+-----------------------------------------------------------------------+
|                   APPLICATION DATABASE SCHEMA (ERD)                    |
+-----------------------------------------------------------------------+

  +-------------------------+
  |     ORGANIZATIONS       |
  |-------------------------|
  | id (PK)      | VARCHAR  |
  | name         | VARCHAR  |
  | password_hash| VARCHAR  |
  | created_at   | TIMESTAMP|
  +------------+------------+
               |
               | 1:N
   +-----------+-------------------+
   |                               |
   v                               v
  +--------------------+    +-----------------------+
  |      USERS         |    | DATABASE_CONNECTIONS  |
  |--------------------|    |-----------------------|
  | id (PK)            |    | id (PK)               |
  | email              |    | organization_id (FK)  |
  | name               |    | name                  |
  | password_hash      |    | db_type               |
  | organization_id(FK)|    | host, port            |
  | is_active          |    | database_name         |
  +----------+---------+    | username              |
             |              | encrypted_password    |
             | 1:N          +-----------+-----------+
             v                          |
  +--------------------+                | 1:1
  |   QUERY_HISTORY    |                v
  |--------------------|    +-----------------------+
  | id (PK)            |    |     SCHEMA_CACHE      |
  | user_id (FK)       |    |-----------------------|
  | connection_id (FK) |    | id (PK)               |
  | natural_lang_query |    | connection_id (FK)    |
  | generated_sql      |    | schema_json           |
  | status             |    | updated_at            |
  | error_message      |    +-----------------------+
  | row_count          |
  | created_at         |
  +--------------------+
"""
    pdf.code_block(erd, 5.5)
    
    pdf.section_title('Table Descriptions')
    pdf.add_table(
        ['Table', 'Purpose', 'Key Fields'],
        [
            ['organizations', 'Multi-tenant isolation', 'name, password_hash'],
            ['users', 'User accounts within orgs', 'email, organization_id'],
            ['database_connections', 'Saved DB configs', 'db_type, host, encrypted_password'],
            ['schema_cache', 'Cached table metadata', 'schema_json (for AI context)'],
            ['query_history', 'Audit trail', 'natural_language_query, generated_sql'],
        ],
        [45, 70, 75]
    )
    
    # Chapter 8: API Endpoints
    pdf.chapter_title('8', 'API Endpoints Reference')
    
    pdf.section_title('Authentication Endpoints')
    pdf.add_table(
        ['Method', 'Endpoint', 'Description'],
        [
            ['POST', '/api/auth/signup', 'Register new user (+ create/join org)'],
            ['POST', '/api/auth/login', 'Authenticate user'],
        ],
        [25, 70, 95]
    )
    
    pdf.section_title('Connection Endpoints')
    pdf.add_table(
        ['Method', 'Endpoint', 'Description'],
        [
            ['POST', '/api/connections/test', 'Test database connection'],
            ['POST', '/api/connections/', 'Save new connection'],
            ['GET', '/api/connections/org/{org_id}', 'List org connections'],
            ['GET', '/api/connections/{id}/schema', 'Extract & cache schema'],
            ['DELETE', '/api/connections/{id}', 'Delete connection'],
        ],
        [25, 80, 85]
    )
    
    pdf.section_title('Query Endpoints')
    pdf.add_table(
        ['Method', 'Endpoint', 'Description'],
        [
            ['POST', '/api/query/', 'Execute NL query pipeline'],
            ['POST', '/api/query/export', 'Export results (CSV/Excel/PDF)'],
            ['GET', '/api/query/history', 'Get user query history'],
        ],
        [25, 70, 95]
    )
    
    # Chapter 9: Data Flow
    pdf.chapter_title('9', 'Data Flow Diagrams')
    
    pdf.section_title('Complete System Data Flow')
    system_flow = """
                                +----------------+
                                |     USER       |
                                |   (Browser)    |
                                +-------+--------+
                                        |
                                        | HTTPS
                                        v
+-----------------------------------------------------------------------+
|                        FRONTEND (Next.js)                              |
|   Login Page   |   Connections   |   Query Page   |   History         |
|                                                                        |
|                        lib/api.ts (HTTP Client)                        |
+--------------------------------+--------------------------------------+
                                 |
                                 | REST API (JSON)
                                 v
+-----------------------------------------------------------------------+
|                        BACKEND (FastAPI)                               |
|                                                                        |
|   +---------------------------------------------------------------+   |
|   |                       API LAYER                                |   |
|   |  /api/auth  |  /api/connections  |  /api/query  |  /api/orgs  |   |
|   +-------------------------------+-------------------------------+   |
|                                   |                                    |
|   +-------------------------------+-------------------------------+   |
|   |                     SERVICE LAYER                              |   |
|   |  Encryption | DB Connector | Schema Extractor | Query Executor |   |
|   +-------------------------------+-------------------------------+   |
|                                   |                                    |
|   +-------------------------------+-------------------------------+   |
|   |                       AI LAYER                                 |   |
|   |        Query Agent (NL->SQL)  |  Analysis Agent (Insights)    |   |
|   +-------------------------------+-------------------------------+   |
+--------------------+----------------------+---------------------------+
                     |                      |
         +-----------+                      +-----------+
         |                                              |
         v                                              v
  +---------------+                            +---------------+
  |   GROQ API    |                            | APP DATABASE  |
  |  (Llama 3.3)  |                            | (PostgreSQL)  |
  |   NL -> SQL   |                            |  - Users      |
  +---------------+                            |  - Connections|
                                               |  - History    |
                                               +-------+-------+
                                                       |
                                                       v
                                               +---------------+
                                               |  CLIENT DBs   |
                                               |  MySQL, PgSQL |
                                               |  SQL Server   |
                                               +---------------+
"""
    pdf.code_block(system_flow, 5)
    
    # Chapter 10: Security
    pdf.chapter_title('10', 'Security Architecture')
    
    pdf.section_title('Security Layers')
    pdf.add_table(
        ['Layer', 'Protection', 'Implementation'],
        [
            ['Transport', 'Encrypt all communications', 'HTTPS/TLS, SSL for DB connections'],
            ['Authentication', 'Verify user identity', 'bcrypt password hashing (factor 12)'],
            ['Authorization', 'Tenant isolation', 'user.org_id == connection.org_id check'],
            ['Data Protection', 'Encrypt stored secrets', 'AES-256 Fernet for DB passwords'],
            ['Query Safety', 'Prevent destructive ops', 'Block DROP/DELETE/UPDATE statements'],
        ],
        [40, 60, 90]
    )
    
    pdf.section_title('Credential Flow')
    cred_flow = """
  User enters DB password
          |
          v
  +---------------+     +---------------+     +---------------+
  | Frontend form |     | Backend API   |     | Fernet        |
  | (plain text)  |---->| connections.py|---->| encrypt()     |
  +---------------+     +---------------+     +-------+-------+
                                                      |
                                              +-------v-------+
                                              | encrypted_    |
                                              | password      |
                                              +-------+-------+
                                                      |
                                              +-------v-------+
                                              | Store in      |
                                              | PostgreSQL    |
                                              +---------------+

  Query Execution (retrieval):

  +---------------+     +---------------+     +---------------+
  | Load from DB  |---->| Fernet        |---->| Build conn    |
  | (encrypted)   |     | decrypt()     |     | URL, execute  |
  +---------------+     +---------------+     +---------------+
"""
    pdf.code_block(cred_flow, 6)
    
    # Chapter 11: Deployment
    pdf.chapter_title('11', 'Deployment Guide')
    
    pdf.section_title('Production Deployment (Render.com)')
    deployment = """
+-----------------------------------------------------------------------+
|                  PRODUCTION DEPLOYMENT (Render.com)                    |
+-----------------------------------------------------------------------+
|                                                                        |
|   +---------------------------------------------------------------+   |
|   |                       Web Services                             |   |
|   |                                                                 |   |
|   |   +---------------------+     +---------------------+          |   |
|   |   |   Backend           |     |   Frontend          |          |   |
|   |   |   (FastAPI)         |<--->|   (Next.js)         |          |   |
|   |   |                     |     |                     |          |   |
|   |   | argo-backend        |     | argo-frontend       |          |   |
|   |   | .onrender.com       |     | .onrender.com       |          |   |
|   |   +----------+----------+     +---------------------+          |   |
|   |              |                                                  |   |
|   |              | Internal connection                              |   |
|   |              v                                                  |   |
|   |   +---------------------+                                       |   |
|   |   |   PostgreSQL        |                                       |   |
|   |   |   Database          |                                       |   |
|   |   |   (dataanalys DB)   |                                       |   |
|   |   +---------------------+                                       |   |
|   +---------------------------------------------------------------+   |
|                                                                        |
+-----------------------------------------------------------------------+
"""
    pdf.code_block(deployment, 5.5)
    
    pdf.section_title('Environment Variables')
    pdf.add_table(
        ['Variable', 'Service', 'Description'],
        [
            ['DATABASE_URL', 'Backend', 'PostgreSQL connection string'],
            ['ENCRYPTION_KEY', 'Backend', 'Fernet key for credential encryption'],
            ['GROQ_API_KEY', 'Backend', 'Groq API key for LLM access'],
            ['FRONTEND_URL', 'Backend', 'Frontend URL for CORS'],
            ['NEXT_PUBLIC_API_URL', 'Frontend', 'Backend API URL'],
        ],
        [55, 35, 100]
    )
    
    pdf.section_title('Local Development Setup')
    setup_cmds = """
# 1. Clone repository
git clone <repository>
cd ARGO_project

# 2. Setup Python virtual environment
python -m venv .venv
.venv\\Scripts\\activate

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
"""
    pdf.code_block(setup_cmds, 7)
    
    # Summary page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 12, 'Summary', ln=True)
    pdf.ln(5)
    
    pdf.body_text(
        'ARGO Analytics provides a complete AI-powered database analytics solution with:'
    )
    pdf.ln(3)
    pdf.bullet_list([
        'Secure multi-tenant architecture with organization-based isolation',
        'Natural language interface powered by Groq Llama 3.3 70B',
        'Multi-database support for major database platforms',
        'End-to-end encryption for stored credentials',
        'Comprehensive audit trail of all queries',
        'Export capabilities for reporting needs',
    ])
    
    pdf.ln(10)
    pdf.body_text(
        'The modular architecture allows easy extension and maintenance, while the clear '
        'separation of concerns ensures security and scalability.'
    )
    
    pdf.ln(20)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f'Document generated: {datetime.now().strftime("%B %d, %Y")}', align='C', ln=True)
    pdf.cell(0, 8, 'ARGO Analytics Platform v1.0.0', align='C')
    
    # Save PDF
    output_path = Path(r"C:\my projects\ARGO_project\docs\ARGO_Analytics_Documentation.pdf")
    pdf.output(str(output_path))
    print(f"PDF generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_documentation()

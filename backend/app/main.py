from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine
from app.models.models import Base
from app.api import organizations, connections, queries, auth

settings = get_settings()
print(f"[STARTUP] DATABASE_URL = {settings.DATABASE_URL}")
print(f"[STARTUP] Engine URL = {engine.url}")

# Create internal DB tables (auto-create for SQLite; use alembic migrate for PostgreSQL)
if "sqlite" in settings.DATABASE_URL:
    Base.metadata.create_all(bind=engine)
else:
    # For PostgreSQL, tables are managed by Alembic migrations.
    # On first run or if DB is empty, auto-create as fallback.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # DB not reachable yet — alembic will handle it

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(connections.router)
app.include_router(queries.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

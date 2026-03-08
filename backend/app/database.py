from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Render uses postgres:// but SQLAlchemy 2.0 requires postgresql://
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread; PostgreSQL benefits from pool settings
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

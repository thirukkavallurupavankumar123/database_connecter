import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Enterprise GenAI Database Analytics Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    FRONTEND_URL: str = ""

    # Groq AI
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Encryption
    ENCRYPTION_KEY: str = ""  # 32-byte Fernet key, generate with: Fernet.generate_key()

    # Query safety
    MAX_ROWS: int = 1000
    QUERY_TIMEOUT_SECONDS: int = 10

    # Internal DB (for storing tenant/connection metadata)
    DATABASE_URL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()

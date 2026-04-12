from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    # ── Google Gemini ──
    GOOGLE_API_KEY: str

    # ── Supabase / Postgres ──
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    # ── Neo4j ──
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # ── Qdrant ──
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # ── Auth ──
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── CORS ──
    CORS_ORIGINS: str = "http://localhost:5173"

    # ── Environment ──
    ENVIRONMENT: str = "development"

    # ── Upload limits ──
    MAX_UPLOAD_SIZE_MB: int = 10

    # ── Email (Resend) ──
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "RAX <onboarding@resend.dev>"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    # Auto-generate a SECRET_KEY for dev so the app doesn't crash,
    # but warn loudly so it gets set in production.
    if not s.SECRET_KEY:
        import logging
        logger = logging.getLogger(__name__)
        if s.ENVIRONMENT == "production":
            raise RuntimeError("SECRET_KEY must be set in production! Add it to your .env file.")
        generated = secrets.token_urlsafe(32)
        logger.warning("SECRET_KEY not set — generated a random key for this session: %s", generated[:8] + "...")
        object.__setattr__(s, "SECRET_KEY", generated)
    return s

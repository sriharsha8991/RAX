import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    from app.db.neo4j_client import init_neo4j_driver
    from app.db.qdrant_client import init_qdrant_client
    from app.db.supabase_client import init_supabase_client

    try:
        init_neo4j_driver()
    except Exception as e:
        logger.warning("Neo4j driver init skipped: %s", e)

    try:
        init_qdrant_client()
    except Exception as e:
        logger.warning("Qdrant client init skipped: %s", e)

    try:
        init_supabase_client()
    except Exception as e:
        logger.warning("Supabase client init skipped: %s", e)

    yield

    # ── Shutdown ──
    from app.db.neo4j_client import close_neo4j_driver
    from app.db.session import close_db_engine

    await close_neo4j_driver()
    await close_db_engine()


settings = get_settings()

app = FastAPI(
    title="RAX — Resume Analysis eXpert",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router Registration ──
from app.api.routes import auth, jobs, resumes, candidates, analysis, feedback  # noqa: E402

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(resumes.router,    prefix="/api/resumes",    tags=["Resumes"])
app.include_router(candidates.router, prefix="/api",            tags=["Candidates"])
app.include_router(analysis.router,   prefix="/api",            tags=["Analysis"])
app.include_router(feedback.router,   prefix="/api/feedback",   tags=["Feedback"])


@app.get("/health")
async def health():
    return {"status": "ok"}

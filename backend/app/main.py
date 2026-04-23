import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup: Initialise and verify all external services ──
    from app.db.neo4j_client import init_neo4j_driver
    from app.db.qdrant_client import init_qdrant_client
    from app.db.supabase_client import init_supabase_client
    from app.db.session import async_engine, _url

    failures: list[str] = []

    # 1. Neo4j
    try:
        driver = init_neo4j_driver()
        await driver.verify_connectivity()
        logger.info("✔ Neo4j connected")
    except Exception as e:
        failures.append(f"Neo4j: {e}")

    # 2. Qdrant
    try:
        qc = init_qdrant_client()
        # get_collections() is called inside init already; if we got here it's alive
        logger.info("✔ Qdrant connected")
    except Exception as e:
        failures.append(f"Qdrant: {e}")

    # 3. Supabase storage (skip when running locally)
    _settings = get_settings()
    if not _settings.USE_LOCAL_SERVICES:
        try:
            init_supabase_client()
            logger.info("✔ Supabase storage client connected")
        except Exception as e:
            failures.append(f"Supabase storage: {e}")
    else:
        logger.info("⏭ Supabase storage skipped (USE_LOCAL_SERVICES=true)")

    # 4. PostgreSQL (local Docker or Supabase pooler)
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✔ PostgreSQL connected")
    except Exception as e:
        failures.append(f"PostgreSQL: {e}")

    if failures:
        for f in failures:
            logger.error("STARTUP CHECK FAILED — %s", f)
        raise RuntimeError(
            f"Application startup aborted — {len(failures)} service(s) unavailable:\n"
            + "\n".join(f"  • {f}" for f in failures)
        )

    logger.info("All startup checks passed — application ready")

    # Auto-create tables when using SQLite (local dev mode)
    if "sqlite" in _url:
        from app.db.base import Base
        from app.models import User, Job, Candidate, Resume, Analysis, Feedback  # noqa: F401
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite tables created for local dev")

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


# ── Request / Response Logging Middleware ──
req_logger = logging.getLogger("app.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        method = request.method
        path = request.url.path
        req_logger.info("%s %s", method, path)

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        log_fn = req_logger.warning if response.status_code >= 400 else req_logger.info
        log_fn("%s %s → %d (%.0fms)", method, path, response.status_code, elapsed_ms)

        return response


app.add_middleware(RequestLoggingMiddleware)


# ── Validation Error Logging ──
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# ── Router Registration ──
from app.api.routes import auth, jobs, resumes, candidates, analysis, feedback, notifications  # noqa: E402
from app.api.routes import sse  # noqa: E402

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(resumes.router,    prefix="/api/resumes",    tags=["Resumes"])
app.include_router(candidates.router, prefix="/api",            tags=["Candidates"])
app.include_router(analysis.router,   prefix="/api",            tags=["Analysis"])
app.include_router(feedback.router,      prefix="/api/feedback",   tags=["Feedback"])
app.include_router(notifications.router, prefix="/api",            tags=["Notifications"])
app.include_router(sse.router,           prefix="/api",            tags=["SSE"])


@app.get("/")
async def root():
    return {"name": "RAX API", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}

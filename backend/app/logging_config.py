"""Centralized logging configuration for RAX backend."""

import logging
import sys

from app.config import get_settings


def setup_logging() -> None:
    """Configure logging for the entire application. Call once at startup."""
    settings = get_settings()

    level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO

    fmt = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    # Reset root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # Console handler (stdout)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
    root.addHandler(console)

    # Quieten noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger("app").info("Logging initialised — level=%s env=%s", logging.getLevelName(level), settings.ENVIRONMENT)

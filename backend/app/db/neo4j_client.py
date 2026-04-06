"""Neo4j async driver singleton."""

from __future__ import annotations

import logging
from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)

_driver: Optional[AsyncDriver] = None


def init_neo4j_driver() -> AsyncDriver:
    """Create the singleton Neo4j async driver. Call at app startup."""
    global _driver
    if _driver is not None:
        return _driver

    settings = get_settings()
    _driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
    )
    logger.info("Neo4j driver initialised → %s", settings.NEO4J_URI)
    return _driver


def get_neo4j_driver() -> AsyncDriver:
    """Return the singleton driver. Raises if not initialised."""
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised — call init_neo4j_driver() first")
    return _driver


async def close_neo4j_driver() -> None:
    """Close the driver on shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")

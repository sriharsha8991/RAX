"""Qdrant vector-DB client singleton."""

from __future__ import annotations

import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import get_settings

logger = logging.getLogger(__name__)

VECTOR_DIM = 768
RESUMES_COLLECTION = "resumes"
JOB_DESCRIPTIONS_COLLECTION = "job_descriptions"

_client: Optional[QdrantClient] = None


def init_qdrant_client() -> QdrantClient:
    """Create the singleton Qdrant client and ensure collections exist. Call at app startup."""
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    _client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )

    # Ensure collections
    existing = {c.name for c in _client.get_collections().collections}
    for name in (RESUMES_COLLECTION, JOB_DESCRIPTIONS_COLLECTION):
        if name not in existing:
            _client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: %s", name)

    logger.info("Qdrant client initialised → %s", settings.QDRANT_URL)
    return _client


def get_qdrant_client() -> QdrantClient:
    """Return the singleton client. Raises if not initialised."""
    if _client is None:
        raise RuntimeError("Qdrant client not initialised — call init_qdrant_client() first")
    return _client

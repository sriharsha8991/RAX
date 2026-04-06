"""Supabase client singleton (used for file storage)."""

from __future__ import annotations

import logging
from typing import Optional

from supabase import Client, create_client

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def init_supabase_client() -> Client:
    """Create the singleton Supabase client. Call at app startup."""
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    logger.info("Supabase client initialised → %s", settings.SUPABASE_URL)
    return _client


def get_supabase() -> Client:
    """Return the singleton Supabase client. Raises if not initialised."""
    if _client is None:
        raise RuntimeError("Supabase client not initialised — call init_supabase_client() first")
    return _client

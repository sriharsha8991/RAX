"""Supabase client singleton (used for file storage)."""

from __future__ import annotations

import logging
from typing import Optional

from supabase import Client, create_client

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def init_supabase_client() -> Client:
    """Create the singleton Supabase client. Call at app startup.

    Uses the service_role key (bypasses RLS) when available,
    falling back to the anon key otherwise.
    """
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.info("Supabase client initialised with service_role key → %s", settings.SUPABASE_URL)
    else:
        logger.warning("Supabase client using anon key — storage uploads may fail due to RLS. Set SUPABASE_SERVICE_ROLE_KEY.")
    _client = create_client(settings.SUPABASE_URL, key)
    return _client


def get_supabase() -> Client:
    """Return the singleton Supabase client. Raises if not initialised."""
    if _client is None:
        raise RuntimeError(
            "Supabase client not initialised — call init_supabase_client() first "
            "or set USE_LOCAL_SERVICES=false in .env"
        )
    return _client

"""Storage abstraction — writes uploaded files to either Supabase Storage or
the local filesystem depending on the USE_LOCAL_SERVICES flag.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)

# Local storage root (created on first write)
_LOCAL_ROOT = Path(__file__).resolve().parent.parent.parent / "uploads"


async def save_file(file_bytes: bytes, file_path: str) -> str:
    """Persist `file_bytes` at logical path `file_path` (e.g. "resumes/<uuid>/file.pdf").

    Returns the path that was actually written (relative path for local mode,
    Supabase storage path for cloud mode).

    Best-effort: logs a warning and returns `file_path` even on failure so the
    caller can continue (the DB record still tracks the intended location).
    """
    settings = get_settings()

    if settings.USE_LOCAL_SERVICES:
        return await _save_local(file_bytes, file_path)
    return await _save_supabase(file_bytes, file_path)


async def _save_local(file_bytes: bytes, file_path: str) -> str:
    target = _LOCAL_ROOT / file_path
    try:
        await asyncio.to_thread(_write_local_sync, target, file_bytes)
        logger.info("Saved file locally → %s (%d bytes)", target, len(file_bytes))
    except Exception as e:
        logger.warning("Local file save failed for %s: %s", file_path, e)
    return file_path


def _write_local_sync(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


async def _save_supabase(file_bytes: bytes, file_path: str) -> str:
    try:
        from app.db.supabase_client import get_supabase

        sb = get_supabase()
        await asyncio.to_thread(sb.storage.from_("resumes").upload, file_path, file_bytes)
        logger.info("Uploaded file to Supabase → %s", file_path)
    except Exception as e:
        logger.warning("Supabase storage upload failed for %s: %s", file_path, e)
    return file_path

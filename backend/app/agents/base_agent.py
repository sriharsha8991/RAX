"""Abstract base class for all pipeline agents."""

from __future__ import annotations

import abc
import asyncio
import logging
from typing import TYPE_CHECKING

from google import genai
from google.genai import types

if TYPE_CHECKING:
    from app.agents.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)

_genai_client: genai.Client | None = None

# Timeout (seconds) applied to every Gemini API call
GEMINI_TIMEOUT = 90

# ── Concurrency limits ────────────────────────────────────────────────────────
# Separate semaphores for generation vs. embedding — they hit different
# endpoints with different rate limits. Embeddings are cheap and fast, so
# they shouldn't be gated by the (smaller) generation slot pool.
_LLM_SEMAPHORE: asyncio.Semaphore | None = None
_EMBED_SEMAPHORE: asyncio.Semaphore | None = None
_LLM_CONCURRENCY = 8      # max simultaneous generate_content calls
_EMBED_CONCURRENCY = 16   # max simultaneous embed_content calls


def _get_llm_semaphore() -> asyncio.Semaphore:
    global _LLM_SEMAPHORE
    if _LLM_SEMAPHORE is None:
        _LLM_SEMAPHORE = asyncio.Semaphore(_LLM_CONCURRENCY)
    return _LLM_SEMAPHORE


def _get_embed_semaphore() -> asyncio.Semaphore:
    global _EMBED_SEMAPHORE
    if _EMBED_SEMAPHORE is None:
        _EMBED_SEMAPHORE = asyncio.Semaphore(_EMBED_CONCURRENCY)
    return _EMBED_SEMAPHORE


# ── Shared generation config ──────────────────────────────────────────────────
# Gemini 2.5 Flash ships with "thinking" enabled by default, which silently
# adds 5–15 seconds of latency per call. We disable it for the whole pipeline —
# every prompt in this codebase is a deterministic extraction / scoring task
# that does NOT benefit from chain-of-thought. This is the single biggest
# latency win for the pipeline.
#
# We also request JSON output natively, which makes parsing more reliable
# (no markdown fences) and slightly reduces output tokens.
def _json_gen_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )


def _get_genai_client() -> genai.Client:
    """Return the singleton google-genai Client, creating it lazily."""
    global _genai_client
    if _genai_client is None:
        from app.config import get_settings
        _genai_client = genai.Client(api_key=get_settings().GOOGLE_API_KEY)
    return _genai_client


def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers from LLM output."""
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return text


class BaseAgent(abc.ABC):
    """Every agent implements `run()` which mutates and returns the PipelineContext."""

    name: str = "BaseAgent"

    _model_name: str = "gemini-2.5-flash"
    _embedding_model_name: str = "gemini-embedding-001"

    @classmethod
    async def call_llm(cls, prompt: str) -> str:
        """Call Gemini with a timeout and concurrency limit."""
        client = _get_genai_client()
        sem = _get_llm_semaphore()
        async with sem:
            try:
                async with asyncio.timeout(GEMINI_TIMEOUT):
                    response = await client.aio.models.generate_content(
                        model=cls._model_name,
                        contents=prompt,
                        config=_json_gen_config(),
                    )
            except TimeoutError:
                raise RuntimeError(f"Gemini API call timed out after {GEMINI_TIMEOUT}s")

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned empty response (possibly blocked by safety filters)")
        return strip_markdown_fences(text)

    @classmethod
    async def call_llm_with_images(
        cls,
        prompt: str,
        images: list[bytes],
        mime_type: str = "image/png",
    ) -> str:
        """Call Gemini multimodal with a text prompt + inline image bytes.

        Used for image-only / "Print to PDF" resumes where native text
        extraction yields nothing. Gemini Flash handles OCR + structured
        extraction in a single call — no Tesseract dependency needed.
        """
        client = _get_genai_client()
        sem = _get_llm_semaphore()
        contents: list = [
            types.Part.from_bytes(data=img, mime_type=mime_type) for img in images
        ]
        contents.append(prompt)
        async with sem:
            try:
                async with asyncio.timeout(GEMINI_TIMEOUT):
                    response = await client.aio.models.generate_content(
                        model=cls._model_name,
                        contents=contents,
                        config=_json_gen_config(),
                    )
            except TimeoutError:
                raise RuntimeError(f"Gemini API call timed out after {GEMINI_TIMEOUT}s")

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned empty response (possibly blocked by safety filters)")
        return strip_markdown_fences(text)

    @classmethod
    async def embed_text(cls, text: str) -> list[float]:
        """Generate a 768-dim embedding using Gemini embedding model."""
        client = _get_genai_client()
        sem = _get_embed_semaphore()
        async with sem:
            try:
                async with asyncio.timeout(GEMINI_TIMEOUT):
                    result = await client.aio.models.embed_content(
                        model=cls._embedding_model_name,
                        contents=text,
                        config=types.EmbedContentConfig(output_dimensionality=768),
                    )
            except TimeoutError:
                raise RuntimeError(f"Gemini embed_content timed out after {GEMINI_TIMEOUT}s")
        return result.embeddings[0].values

    @abc.abstractmethod
    async def run(self, ctx: "PipelineContext") -> "PipelineContext":
        """Execute this agent's logic and return the updated context."""
        ...

    def __repr__(self) -> str:
        return f"<{self.name}>"

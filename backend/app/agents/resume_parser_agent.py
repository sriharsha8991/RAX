"""Stage 1: Extract raw text from PDF/DOCX and parse into structured JSON via Gemini.

Strategy (two paths, no Tesseract dependency):

1. **Fast path â€” native text layer.** PyMuPDF extracts text in a few ms.
   Send text to Gemini â†’ JSON. Handles ~95% of resumes.

2. **Vision fallback â€” render pages to PNG.** When the PDF has no text
   layer (scanned resumes, "Microsoft Print to PDF" vector output, etc.),
   render each page to a ~150 DPI PNG and send the images directly to
   Gemini multimodal. Gemini Flash does OCR + structured extraction in a
   single call, returning the same JSON schema. No OCR dependency.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging

from app.agents.base_agent import BaseAgent
from app.agents.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)

# â”€â”€ Prompts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_JSON_SCHEMA = """{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "skills": [{{"name": "string", "years": integer_or_0, "proficiency": "beginner|intermediate|expert"}}],
  "experience": [{{"title": "string", "company": "string", "duration": "string", "description": "string"}}],
  "education": [{{"degree": "string", "field": "string", "institution": "string", "year": integer_or_0}}]
}}"""

PARSE_PROMPT = f"""You are a resume parser. Extract structured data from the following resume text.

Return ONLY valid JSON with this exact schema (no markdown fences):
{_JSON_SCHEMA}

If a field is unknown, use empty string or 0. Do not invent data.

Resume text:
---
{{resume_text}}
---
"""

VISION_PROMPT = f"""You are a resume parser. The attached images are the pages
of a resume PDF that has no machine-readable text layer. Read the text from
the images and extract structured data.

Return ONLY valid JSON with this exact schema (no markdown fences):
{_JSON_SCHEMA}

If a field is unknown, use empty string or 0. Do not invent data.
"""

# Page image render DPI â€” 150 balances clarity vs. payload size.
# A typical single-page resume at 150 DPI is ~200-400 KB PNG.
_RENDER_DPI = 150

# Hard cap on pages sent to Gemini to control cost/latency.
_MAX_PAGES_TO_RENDER = 8


# â”€â”€ PDF helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _extract_native_text(file_bytes: bytes) -> str:
    """Fast path: pull text layer out of a PDF (5-15 ms/page)."""
    import pymupdf

    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        parts = [page.get_text("text") or "" for page in doc]
    return "\n".join(parts).strip()


def _render_pdf_to_pngs(file_bytes: bytes, dpi: int = _RENDER_DPI) -> list[bytes]:
    """Render each PDF page to a PNG (bytes). Used for the vision fallback."""
    import pymupdf

    images: list[bytes] = []
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        total = len(doc)
        for idx, page in enumerate(doc):
            if idx >= _MAX_PAGES_TO_RENDER:
                logger.warning(
                    "PDF has %d pages â€” truncating to first %d for Gemini vision",
                    total, _MAX_PAGES_TO_RENDER,
                )
                break
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            images.append(pix.tobytes("png"))
    return images


def _extract_docx_text(file_bytes: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def _parsed_to_text(parsed: dict) -> str:
    """Flatten a parsed-resume dict into a single text blob so downstream
    agents (embedding, semantic matching) still have something to work with
    even when the text came only from vision."""
    lines: list[str] = []
    if parsed.get("name"):
        lines.append(str(parsed["name"]))
    for key in ("email", "phone"):
        if parsed.get(key):
            lines.append(str(parsed[key]))
    for s in parsed.get("skills", []) or []:
        if isinstance(s, dict) and s.get("name"):
            lines.append(str(s["name"]))
    for e in parsed.get("experience", []) or []:
        if isinstance(e, dict):
            bits = [e.get("title", ""), e.get("company", ""), e.get("duration", ""), e.get("description", "")]
            lines.append(" â€” ".join(str(b) for b in bits if b))
    for ed in parsed.get("education", []) or []:
        if isinstance(ed, dict):
            bits = [
                ed.get("degree", ""),
                ed.get("field", ""),
                ed.get("institution", ""),
                str(ed.get("year", "") or ""),
            ]
            lines.append(" â€” ".join(str(b) for b in bits if b))
    return "\n".join(lines).strip()


# â”€â”€ Agent â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class ResumeParserAgent(BaseAgent):
    name = "ResumeParserAgent"

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.current_stage = "parsing"
        logger.info("ResumeParserAgent: starting parse for resume %s", ctx.resume_id)

        if not ctx.file_bytes and not ctx.raw_text:
            ctx.error = "No file bytes or raw text available for parsing"
            return ctx

        ext = ctx.filename.rsplit(".", 1)[-1].lower() if "." in ctx.filename else ""

        # â”€â”€ DOCX: always text-only â”€â”€
        if ext == "docx":
            try:
                ctx.raw_text = await asyncio.to_thread(_extract_docx_text, ctx.file_bytes)
                logger.info(
                    "ResumeParserAgent: extracted %d chars from %s",
                    len(ctx.raw_text), ctx.filename,
                )
            except Exception as exc:
                logger.error("DOCX extraction failed for %s: %s", ctx.filename, exc)
                ctx.error = f"DOCX extraction failed: {exc}"
                return ctx
            return await self._parse_text(ctx)

        # â”€â”€ PDF: native text first, vision fallback â”€â”€
        if ext == "pdf":
            # 1. Try native text layer
            try:
                native_text = await asyncio.to_thread(_extract_native_text, ctx.file_bytes)
            except Exception as exc:
                logger.error(
                    "PyMuPDF native text extraction crashed for %s: %s",
                    ctx.filename, exc,
                )
                native_text = ""

            if native_text:
                ctx.raw_text = native_text
                logger.info(
                    "ResumeParserAgent: extracted %d chars from %s (native text layer)",
                    len(native_text), ctx.filename,
                )
                return await self._parse_text(ctx)

            # 2. Vision fallback â€” render pages and send to Gemini multimodal
            logger.info(
                "ResumeParserAgent: no text layer in %s â€” using Gemini vision fallback",
                ctx.filename,
            )
            try:
                images = await asyncio.to_thread(_render_pdf_to_pngs, ctx.file_bytes)
            except Exception as exc:
                logger.error("PDF-to-image rendering failed for %s: %s", ctx.filename, exc)
                ctx.error = f"PDF rendering failed: {exc}"
                return ctx

            if not images:
                ctx.error = "PDF has no pages to render"
                return ctx

            logger.info(
                "ResumeParserAgent: rendered %d page(s) of %s â†’ sending to Gemini vision",
                len(images), ctx.filename,
            )
            try:
                response = await self.call_llm_with_images(VISION_PROMPT, images)
                ctx.parsed_resume = json.loads(response)
                ctx.raw_text = _parsed_to_text(ctx.parsed_resume)
                logger.info(
                    "ResumeParserAgent: vision parse succeeded for %s "
                    "(%d skills, %d experiences)",
                    ctx.filename,
                    len(ctx.parsed_resume.get("skills", [])),
                    len(ctx.parsed_resume.get("experience", [])),
                )
            except (json.JSONDecodeError, IndexError) as exc:
                logger.error(
                    "ResumeParserAgent: vision response JSON invalid for %s: %s",
                    ctx.filename, exc,
                )
                ctx.error = f"Vision parse failed (invalid JSON): {exc}"
            except RuntimeError as exc:
                logger.error(
                    "ResumeParserAgent: Gemini vision call failed for %s: %s",
                    ctx.filename, exc,
                )
                ctx.error = str(exc)
            return ctx

        ctx.error = f"Unsupported file type: '.{ext}'. Only PDF and DOCX are supported."
        logger.warning("ResumeParserAgent: %s", ctx.error)
        return ctx

    # â”€â”€ helpers â”€â”€
    async def _parse_text(self, ctx: PipelineContext) -> PipelineContext:
        """Send `ctx.raw_text` to Gemini with the JSON schema prompt."""
        prompt = PARSE_PROMPT.format(resume_text=ctx.raw_text[:15000])
        try:
            response = await self.call_llm(prompt)
            ctx.parsed_resume = json.loads(response)
        except (json.JSONDecodeError, IndexError) as exc:
            logger.error("ResumeParserAgent: failed to parse Gemini response: %s", exc)
            ctx.error = f"Resume parsing failed: {exc}"
        except RuntimeError as exc:
            logger.error("ResumeParserAgent: Gemini call failed: %s", exc)
            ctx.error = str(exc)
        return ctx


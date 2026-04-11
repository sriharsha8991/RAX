"""Stage 1: Extract raw text from PDF/DOCX and parse into structured JSON via Gemini."""

from __future__ import annotations

import asyncio
import io
import json
import logging

from app.agents.base_agent import BaseAgent
from app.agents.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)

PARSE_PROMPT = """You are a resume parser. Extract structured data from the following resume text.

Return ONLY valid JSON with this exact schema (no markdown fences):
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "skills": [{{"name": "string", "years": integer_or_0, "proficiency": "beginner|intermediate|expert"}}],
  "experience": [{{"title": "string", "company": "string", "duration": "string", "description": "string"}}],
  "education": [{{"degree": "string", "field": "string", "institution": "string", "year": integer_or_0}}]
}}

If a field is unknown, use empty string or 0. Do not invent data.

Resume text:
---
{resume_text}
---
"""


def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from PDF or DOCX file bytes.

    Raises ValueError for unsupported file types.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if ext in ("docx",):
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    raise ValueError(f"Unsupported file type: '.{ext}'. Only PDF and DOCX are supported.")


class ResumeParserAgent(BaseAgent):
    name = "ResumeParserAgent"

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.current_stage = "parsing"
        logger.info("ResumeParserAgent: starting parse for resume %s", ctx.resume_id)

        # Extract raw text from file bytes if raw_text is not already provided
        if not ctx.raw_text and ctx.file_bytes:
            try:
                ctx.raw_text = await asyncio.to_thread(_extract_text, ctx.file_bytes, ctx.filename)
                logger.info("ResumeParserAgent: extracted %d chars from %s", len(ctx.raw_text), ctx.filename)
            except ValueError as exc:
                ctx.error = str(exc)
                return ctx
            except Exception as exc:
                logger.error("ResumeParserAgent: text extraction failed: %s", exc)
                ctx.error = f"File extraction failed: {exc}"
                return ctx

        if not ctx.raw_text:
            ctx.error = "No raw text available for parsing"
            return ctx

        prompt = PARSE_PROMPT.format(resume_text=ctx.raw_text[:15000])  # truncate safety

        try:
            text = await self.call_llm(prompt)
            ctx.parsed_resume = json.loads(text)
        except (json.JSONDecodeError, IndexError) as exc:
            logger.error("ResumeParserAgent: failed to parse Gemini response: %s", exc)
            ctx.error = f"Resume parsing failed: {exc}"
        except RuntimeError as exc:
            logger.error("ResumeParserAgent: Gemini call failed: %s", exc)
            ctx.error = str(exc)

        return ctx

"""Shared context object passed through the entire agent pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineContext:
    """Mutable context that flows through every agent in sequence.

    Each agent reads what it needs, writes its output, and passes it forward.
    """

    # ── Identifiers (set at pipeline start) ──
    resume_id: str = ""
    job_id: str = ""

    # ── Job data (loaded at pipeline start) ──
    job_title: str = ""
    job_description: str = ""
    job_requirements: dict[str, Any] = field(default_factory=dict)

    # ── Input: raw file bytes (PDF/DOCX) for text extraction ──
    file_bytes: bytes = b""
    filename: str = ""

    # ── Stage 1: ResumeParserAgent output ──
    raw_text: str = ""
    parsed_resume: dict[str, Any] = field(default_factory=dict)
    # Expected shape:
    # {
    #   "name": str,
    #   "email": str,
    #   "phone": str,
    #   "skills": [{"name": str, "years": int, "proficiency": str}],
    #   "experience": [{"title": str, "company": str, "duration": str, "description": str}],
    #   "education": [{"degree": str, "field": str, "institution": str, "year": int}]
    # }

    # ── Stage 1b: ExperienceExtractorAgent output (LLM judge) ──
    enriched_experience: dict[str, Any] = field(default_factory=dict)
    # Expected shape:
    # {
    #   "total_years_experience": float,
    #   "seniority_level": str,
    #   "experience_entries": [{"title", "company", "start_date", "end_date", "duration_months", "key_technologies"}],
    #   "skill_experience": [{"skill", "estimated_years", "evidence"}]
    # }

    # ── Stage 2: BiasFilterAgent output ──
    filtered_resume: dict[str, Any] = field(default_factory=dict)
    # Same shape as parsed_resume but with:
    #   name → "[CANDIDATE_ID]", institution → "[UNIVERSITY]",
    #   gender/nationality signals removed

    # ── Stage 3a: GraphIngestionAgent output ──
    graph_node_id: str = ""  # Neo4j node ID for the candidate

    # ── Stage 3b: EmbeddingAgent output ──
    qdrant_point_id: str = ""  # Qdrant point ID for the resume vector

    # ── Stage 4: HybridMatchingAgent output ──
    match_result: dict[str, Any] = field(default_factory=dict)
    # Expected shape:
    # {
    #   "structural_score": float,    # 0.0–1.0 (Neo4j graph traversal)
    #   "semantic_score": float,      # 0.0–1.0 (Qdrant cosine similarity)
    #   "experience_score": float,    # 0.0–1.0
    #   "education_score": float,     # 0.0–1.0
    #   "hybrid_score": float,        # weighted fusion
    #   "matched_skills": list,
    #   "similar_skills": list,
    #   "skill_gaps": list,
    #   "graph_paths": list,          # explainability paths
    # }

    # ── Stage 5: ScoringAgent output ──
    analysis: dict[str, Any] = field(default_factory=dict)
    # Expected shape:
    # {
    #   "overall_score": int,         # 0–100
    #   "skills_score": int,
    #   "experience_score": int,
    #   "education_score": int,
    #   "strengths": [str],
    #   "gaps": [str],
    #   "explanation": str,
    # }

    # ── Pipeline metadata ──
    current_stage: str = "queued"
    error: str | None = None

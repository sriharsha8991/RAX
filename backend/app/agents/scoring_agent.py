"""Stage 5: Generate multi-dimensional scores + natural language explanation via Gemini."""

from __future__ import annotations

import json
import logging

from app.agents.base_agent import BaseAgent
from app.agents.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)

SCORING_PROMPT = """You are an expert hiring evaluator. Evaluate a candidate's resume against a specific job posting and produce a detailed scoring assessment.

**Job Title:** {job_title}

**Job Description:**
{job_description}

**Job Requirements:**
{job_requirements}

**Anonymized Resume (structured):**
{filtered_resume}

**Verified Experience Data (extracted by LLM judge — use this as the authoritative source for experience):**
{enriched_experience}

**Supplementary Hybrid Match Data (graph + vector analysis):**
{match_result}

EVALUATION INSTRUCTIONS:
1. **Skills Score**: Compare the candidate's skills directly against the job requirements. Count how many required skills appear in the resume (exact or closely related). Score higher when the candidate has most required skills. Use the skill_experience data for accurate years-of-experience per skill.
2. **Experience Score**: Use the verified experience data (total_years_experience, seniority_level, experience_entries with duration_months) as the primary source. Assess whether the candidate's work experience is relevant to the job description. Consider total years, seniority level, and domain relevance.
3. **Education Score**: Evaluate whether the candidate's education aligns with job requirements (degree level, field of study).
4. **Overall Score**: Weighted combination — skills (40%), experience (35%), education (25%). Adjust if the candidate is exceptionally strong or weak in a key area.

IMPORTANT: Base your scores PRIMARILY on comparing the resume content against the job title, description, and requirements. Use the verified experience data for accurate experience assessment. The hybrid match data is supplementary — use it to support your assessment but do not rely on it if it seems incomplete or has default values.

Generate a JSON response with this exact schema (no markdown fences):
{{
  "overall_score": <integer 0-100>,
  "skills_score": <integer 0-100>,
  "experience_score": <integer 0-100>,
  "education_score": <integer 0-100>,
  "strengths": ["strength 1", "strength 2", ...],
  "gaps": ["gap 1", "gap 2", ...],
  "explanation": "<2-3 sentence natural language explanation referencing specific skill matches from resume vs job requirements, experience relevance, and education fit>"
}}
"""


class ScoringAgent(BaseAgent):
    name = "ScoringAgent"

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.current_stage = "scoring"
        logger.info("ScoringAgent: generating scores for resume %s", ctx.resume_id)

        # If no match data, provide defaults so scoring can still proceed
        if not ctx.match_result:
            ctx.match_result = {
                "structural_score": 0.5,
                "semantic_score": 0.5,
                "experience_score": 0.5,
                "education_score": 0.5,
                "hybrid_score": 0.5,
                "matched_skills": [],
                "similar_skills": [],
                "skill_gaps": [],
                "graph_paths": [],
            }

        prompt = SCORING_PROMPT.format(
            job_title=ctx.job_title or "Not specified",
            job_description=ctx.job_description or "Not specified",
            job_requirements=json.dumps(ctx.job_requirements, indent=2) if ctx.job_requirements else "Not specified",
            enriched_experience=json.dumps(ctx.enriched_experience, indent=2) if ctx.enriched_experience else "Not available — use resume entries for best estimate",
            match_result=json.dumps(ctx.match_result, indent=2),
            filtered_resume=json.dumps(ctx.filtered_resume, indent=2),
        )

        try:
            text = await self.call_llm(prompt)
            ctx.analysis = json.loads(text)
            # Copy match data into analysis so FeedbackAgent can access it
            ctx.analysis["matched_skills"] = ctx.match_result.get("matched_skills", [])
            ctx.analysis["similar_skills"] = ctx.match_result.get("similar_skills", [])
            ctx.analysis["skill_gaps"] = ctx.match_result.get("skill_gaps", [])
            ctx.analysis["graph_paths"] = ctx.match_result.get("graph_paths", [])
            ctx.analysis["semantic_similarity"] = ctx.match_result.get("semantic_score", 0.0)
            ctx.analysis["structural_match"] = ctx.match_result.get("structural_score", 0.0)
        except (json.JSONDecodeError, IndexError) as exc:
            logger.error("ScoringAgent: failed to parse response: %s", exc)
            ctx.error = f"Scoring failed: {exc}"
        except RuntimeError as exc:
            logger.error("ScoringAgent: Gemini call failed: %s", exc)
            ctx.error = str(exc)

        return ctx

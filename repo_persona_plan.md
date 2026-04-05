# RAX — AI Pipeline Persona Plan (Person 2)

> **Owner:** Person 2 — AI Pipeline (Gemini, Neo4j Graph Agents, Qdrant Embedding, WebSocket)
> **Scope:** `backend/app/agents/`, `backend/app/api/routes/ws.py`, AI-related deps
> **Compatibility:** Depends on Person 1's DB layer (`db/session.py`, `db/neo4j_client.py`, `db/qdrant_client.py`, models). Exposes agents consumed by Person 1's routes + Person 3's WebSocket UI.

---

## Interface Contract with Other Personas

### What Person 1 (Backend Core) provides to us:
- `backend/app/db/session.py` — `get_db` async dependency (SQLAlchemy session)
- `backend/app/db/neo4j_client.py` — `get_neo4j_session()` async context manager
- `backend/app/db/qdrant_client.py` — `get_qdrant_client()` singleton
- `backend/app/models/` — SQLAlchemy models (resume, analysis, feedback)
- `backend/app/config.py` — `Settings` with all env vars

### What we provide to Person 1 (Backend Core):
- `PipelineOrchestrator.run(resume_id, job_id, db, neo4j, qdrant)` — called as BackgroundTask from `resumes.py`
- `FeedbackAgent.run(resume_id, job_id, db, neo4j)` — called on-demand from `feedback.py`
- `EmbeddingAgent.embed_job(job_id, text, qdrant)` — called from `jobs.py` on job create
- `GraphIngestionAgent.ingest_job(job_id, requirements, neo4j)` — called from `jobs.py` on job create

### What we provide to Person 3 (Frontend):
- WebSocket endpoint `WS /ws/pipeline/{job_id}` — emits `{ resume_id, stage, status, timestamp }`

---

## Phased Plan

### Phase 1: Foundation + Standalone Agent Skeleton ✅
> **Goal:** Backend scaffold with agents directory, PipelineContext, BaseAgent, config, and deps — fully runnable independent of Person 1's code.
> **Files created:**
> - `backend/requirements.txt`
> - `backend/app/__init__.py`, `main.py`, `config.py`
> - `backend/app/agents/__init__.py`, `pipeline_context.py`, `base_agent.py`
> - `backend/app/agents/resume_parser_agent.py` (skeleton)
> - `backend/app/agents/bias_filter_agent.py` (skeleton)
> - `backend/app/agents/graph_ingestion_agent.py` (skeleton)
> - `backend/app/agents/embedding_agent.py` (skeleton)
> - `backend/app/agents/hybrid_matching_agent.py` (skeleton)
> - `backend/app/agents/scoring_agent.py` (skeleton)
> - `backend/app/agents/feedback_agent.py` (skeleton)
> - `backend/app/agents/orchestrator.py` (skeleton)

### Phase 2: ResumeParserAgent + BiasFilterAgent (Full Implementation)
> **Goal:** Working text extraction (PDF/DOCX) + Gemini structured JSON parsing + bias anonymization.
> **Depends on:** Phase 1 only (no DB needed — operates on file bytes + returns dataclass)
> **Test:** Feed a sample PDF → get back structured JSON → get back anonymized JSON

### Phase 3: GraphIngestionAgent (Full Implementation)
> **Goal:** Decompose parsed resume into Neo4j nodes + relationships. Also handle JD ingestion.
> **Depends on:** Phase 1, Neo4j running (`docker-compose up neo4j`)
> **Test:** Feed parsed JSON → verify nodes/edges in Neo4j browser

### Phase 4: EmbeddingAgent (Full Implementation)
> **Goal:** Embed resume/JD text via Gemini `text-embedding-004` → upsert into Qdrant collections.
> **Depends on:** Phase 1, Qdrant running (`docker-compose up qdrant`), Gemini API key
> **Test:** Feed text → verify vector stored in Qdrant dashboard

### Phase 5: HybridMatchingAgent + ScoringAgent (Full Implementation)
> **Goal:** Cypher graph traversal + Qdrant cosine similarity → fused score → Gemini explanation.
> **Depends on:** Phases 3 + 4 (graph + vectors must exist)
> **Test:** Given a candidate + job in graph/vector → get hybrid score + explanation

### Phase 6: FeedbackAgent + PipelineOrchestrator (Full Implementation)
> **Goal:** On-demand feedback generation. Orchestrator wires all agents in sequence with status tracking.
> **Depends on:** Phases 2–5 complete
> **Test:** Upload PDF → full pipeline runs → analysis record created

### Phase 7: WebSocket Real-Time Broadcasting
> **Goal:** `WS /ws/pipeline/{job_id}` endpoint with in-memory pub/sub. Orchestrator publishes stage events.
> **Depends on:** Phase 6
> **Test:** Connect WS client → upload resume → receive stage-by-stage events

### Phase 8: Integration with Person 1's Routes
> **Goal:** Wire agents into Person 1's API routes. Verify end-to-end flow with actual DB.
> **Depends on:** Person 1's routes + models ready
> **Test:** Full API call: `POST /resumes` → pipeline → `GET /candidates` → ranked list

---

## Status Tracker

| Phase | Status | Notes |
|---|---|---|
| 1 | ✅ Complete | Foundation scaffold |
| 2 | Not started | |
| 3 | Not started | |
| 4 | Not started | |
| 5 | Not started | |
| 6 | Not started | |
| 7 | Not started | |
| 8 | Not started | Blocked on Person 1 |

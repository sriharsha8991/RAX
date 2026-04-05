# RAX — Backend Core Persona Plan (Person 1)

> **Owner:** Person 1 — Backend Core (FastAPI, Supabase, Auth, DB Models, CRUD APIs)
> **Scope:** `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/api/`, `backend/alembic/`
> **Do NOT touch:** `backend/app/agents/` (Person 2 owns this)

---

## What Already Exists (Built by Person 2 — Phase 1)

Person 2 has scaffolded the backend. You are building **on top of** their foundation:

```
backend/
├── requirements.txt          # ✅ exists — ADD your deps here (don't replace)
├── app/
│   ├── __init__.py           # ✅ exists
│   ├── config.py             # ✅ exists — Settings with all env vars (shared)
│   ├── main.py               # ✅ exists — FastAPI app, CORS, /health (ADD your routers here)
│   └── agents/               # ❌ DO NOT TOUCH — Person 2's domain
│       ├── pipeline_context.py
│       ├── base_agent.py
│       ├── resume_parser_agent.py
│       ├── bias_filter_agent.py
│       ├── graph_ingestion_agent.py
│       ├── embedding_agent.py
│       ├── hybrid_matching_agent.py
│       ├── scoring_agent.py
│       ├── feedback_agent.py
│       └── orchestrator.py
```

---

## Interface Contract

### What you provide to Person 2 (AI Pipeline):
- `backend/app/db/session.py` — `get_db()` async dependency returning SQLAlchemy `AsyncSession`
- `backend/app/db/neo4j_client.py` — `get_neo4j_driver()` returning async Neo4j driver
- `backend/app/db/qdrant_client.py` — `get_qdrant_client()` returning Qdrant client instance
- `backend/app/models/resume.py` — Resume model (Person 2 Updates `status` field during pipeline)
- `backend/app/models/analysis.py` — Analysis model (Person 2 writes scoring results here)
- `backend/app/models/feedback.py` — Feedback model (Person 2 writes feedback here)

### What you consume from Person 2 (AI Pipeline):
- `PipelineOrchestrator.run(resume_id, job_id, db, neo4j, qdrant)` — call as `BackgroundTask` from `POST /resumes`
- `FeedbackAgent.run(resume_id, job_id, db, neo4j)` — call on-demand from `POST /feedback`
- `EmbeddingAgent.embed_job(job_id, text, qdrant)` — call from `POST /jobs` after job creation
- `GraphIngestionAgent.ingest_job(job_id, requirements, neo4j)` — call from `POST /jobs` after job creation

### What you provide to Person 3 (Frontend):
- All REST API endpoints (auth, jobs, resumes, candidates, analysis, feedback)
- JWT token format: `{ sub: user_id, role: "recruiter"|"hiring_manager" }`

---

## Phased Plan

### Phase 1: Database Layer + Client Setup
> **Goal:** SQLAlchemy async session, Supabase client, Neo4j driver, Qdrant client — all wired up.
> **Depends on:** Person 2's `config.py` (already exists)
> **Creates:**
> ```
> backend/app/db/
> ├── __init__.py
> ├── session.py           # async engine + get_db() dependency
> ├── base.py              # DeclarativeBase
> ├── supabase_client.py   # Supabase SDK init (for file storage)
> ├── neo4j_client.py      # AsyncGraphDatabase.driver() + get_neo4j_driver()
> └── qdrant_client.py     # QdrantClient() + get_qdrant_client()
> ```
>
> **Key details:**
> - `DATABASE_URL` from `config.py` → `create_async_engine(url, echo=False)`
> - Supabase needs `?sslmode=require` on the connection string
> - Neo4j: `AsyncGraphDatabase.driver(NEO4J_URI, auth=(user, pass))`
> - Qdrant: `QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)`
> - Add deps to `requirements.txt`: `sqlalchemy[asyncio]`, `asyncpg`, `supabase`, `alembic`
>
> **Test:** Import each client, verify connection handshake (Neo4j `RETURN 1`, Qdrant `/healthz`)

### Phase 2: SQLAlchemy Models
> **Goal:** All 6 database models defined with relationships.
> **Depends on:** Phase 1 (`base.py`)
> **Creates:**
> ```
> backend/app/models/
> ├── __init__.py          # re-export all models
> ├── user.py              # id, email, hashed_password, full_name, role, created_at
> ├── job.py               # id, title, description, requirements_raw, embedding_id, created_by(FK→user), status, created_at
> ├── candidate.py         # id, name(nullable), email, phone, neo4j_node_id, created_at
> ├── resume.py            # id, candidate_id(FK), job_id(FK), file_path, raw_text, parsed_json(JSONB), anonymized_json(JSONB), embedding_id, pipeline_status(enum), created_at
> ├── analysis.py          # id, resume_id(FK), job_id(FK), overall_score, skills_score, experience_score, education_score, semantic_similarity, structural_match, explanation, strengths(JSONB), gaps(JSONB), graph_paths(JSONB), created_at
> └── feedback.py          # id, candidate_id(FK), job_id(FK), resume_id(FK), content, sent_at, created_at
> ```
>
> **Pipeline status enum values:** `uploaded`, `parsing`, `filtering`, `ingesting`, `embedding`, `matching`, `scoring`, `completed`, `failed`
>
> **Test:** `alembic revision --autogenerate` succeeds

### Phase 3: Alembic Migrations
> **Goal:** Generate + apply initial migration to Supabase Postgres.
> **Depends on:** Phase 2
> **Creates:**
> ```
> backend/alembic/
> ├── alembic.ini
> ├── env.py               # async-aware, reads DATABASE_URL from config
> └── versions/
>     └── 001_initial.py   # auto-generated from models
> ```
>
> **Test:** `alembic upgrade head` → tables visible in Supabase dashboard

### Phase 4: Pydantic Schemas
> **Goal:** Request/response schemas for all API endpoints.
> **Depends on:** Phase 2 (model field reference)
> **Creates:**
> ```
> backend/app/schemas/
> ├── __init__.py
> ├── user.py              # UserCreate, UserLogin, UserResponse, TokenResponse
> ├── job.py               # JobCreate, JobUpdate, JobResponse, JobListResponse
> ├── candidate.py         # CandidateResponse, CandidateListResponse
> ├── resume.py            # ResumeUploadResponse, ResumeStatusResponse
> ├── analysis.py          # AnalysisResponse (includes strengths, gaps, explanation)
> └── feedback.py          # FeedbackCreate, FeedbackResponse
> ```
>
> **Test:** Instantiate each schema with sample data

### Phase 5: Auth (JWT)
> **Goal:** Register + login endpoints, `get_current_user` dependency.
> **Depends on:** Phases 1 + 2 + 4
> **Creates:**
> ```
> backend/app/api/
> ├── __init__.py
> ├── dependencies.py      # get_current_user(token) → User, require_role("recruiter")
> └── routes/
>     ├── __init__.py
>     └── auth.py          # POST /auth/register, POST /auth/login
> ```
>
> **Key details:**
> - `python-jose[cryptography]` for JWT encode/decode
> - `passlib[bcrypt]` for password hashing
> - Token payload: `{ sub: str(user.id), role: user.role, exp: datetime }`
> - Add deps to `requirements.txt`: `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`
>
> **Test:** Register → login → access protected endpoint → verify role guard

### Phase 6: CRUD API Routes
> **Goal:** All REST endpoints for jobs, resumes, candidates, analysis, feedback.
> **Depends on:** Phase 5 (auth guard)
> **Creates:**
> ```
> backend/app/api/routes/
> ├── jobs.py              # GET /jobs, POST /jobs, GET /jobs/{id}, PUT /jobs/{id}
> ├── resumes.py           # POST /resumes/upload (multipart), GET /resumes/{id}/status
> ├── candidates.py        # GET /jobs/{job_id}/candidates (ranked by score)
> ├── analysis.py          # GET /resumes/{resume_id}/analysis
> └── feedback.py          # POST /feedback/{candidate_id}/{job_id}, GET /feedback/{id}
> ```
>
> **Key integration points with Person 2:**
> - `POST /jobs` → after DB insert, call `EmbeddingAgent.embed_job()` + `GraphIngestionAgent.ingest_job()`
> - `POST /resumes/upload` → after file save, call `PipelineOrchestrator.run()` as `BackgroundTask`
> - `POST /feedback` → call `FeedbackAgent.run()` on demand
> - If Person 2's agents aren't ready yet, wrap calls in try/except with logging — don't block API
>
> **File storage:**
> - Upload PDF/DOCX → store in Supabase Storage (`resumes` bucket) via `supabase_client`
> - Save `file_path` (Supabase storage path) in `resume` record
>
> **Test:** CRUD cycle for each entity with `httpx.AsyncClient`

### Phase 7: Register Routers in main.py
> **Goal:** Wire all route modules into FastAPI app. Add lifespan for DB/client init+cleanup.
> **Depends on:** Phase 6
> **Modifies:** `backend/app/main.py` (Person 2 created this — ADD routers, don't replace)
>
> **Add to main.py:**
> ```python
> from app.api.routes import auth, jobs, resumes, candidates, analysis, feedback
> app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
> app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
> app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
> app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
> app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
> app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
> ```
>
> **Add lifespan events:** init DB engine, Neo4j driver, Qdrant client; cleanup on shutdown
>
> **Test:** `uvicorn app.main:app --reload` → `/docs` shows all endpoints

### Phase 8: Unit Tests
> **Goal:** Full test coverage for routes + auth + DB operations.
> **Depends on:** Phase 7
> **Creates:**
> ```
> backend/tests/
> ├── conftest.py          # test DB, test client, auth fixtures
> ├── test_auth.py         # register, login, token validation, role guard
> ├── test_jobs.py         # CRUD + JD embedding trigger
> ├── test_resumes.py      # upload + pipeline trigger
> ├── test_candidates.py   # ranked listing
> └── test_feedback.py     # feedback generation
> ```
>
> **Test:** `pytest backend/tests/ -v`

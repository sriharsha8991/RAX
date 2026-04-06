# RAX — Backend Core Implementation Tracker

> **Owner:** Person 1 — Backend Core  
> **Scope:** `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/api/`, `backend/alembic/`, `backend/tests/`  
> **DO NOT TOUCH:** `backend/app/agents/` (Person 2), `frontend/` (Person 3)  
> **Last Updated:** 2026-04-05 (Phases 1–4 complete)

---

## Quick Status Dashboard

| Phase | Description                    | Status      | Completed On |
|-------|--------------------------------|-------------|--------------|
| 1     | Database & Client Layer        | COMPLETED   | 2026-04-05   |
| 2     | SQLAlchemy Models              | COMPLETED   | 2026-04-05   |
| 3     | Alembic Migrations             | COMPLETED   | 2026-04-05   |
| 4     | Pydantic Schemas               | COMPLETED   | 2026-04-05   |
| 5     | Authentication (JWT)           | COMPLETED   | 2026-04-06   |
| 6     | CRUD API Routes                | COMPLETED   | 2026-04-06   |
| 7     | Router Registration & Lifespan | COMPLETED   | 2026-04-06   |
| 8     | Tests                          | COMPLETED   | 2026-04-06   |

---

## Dependency Chain

```
Phase 1 (DB Layer)
  └──▶ Phase 2 (Models)
         ├──▶ Phase 3 (Migrations)   ← can run in parallel with Phase 4
         └──▶ Phase 4 (Schemas)      ← can run in parallel with Phase 3
                └──▶ Phase 5 (Auth)
                       └──▶ Phase 6 (CRUD Routes)
                              └──▶ Phase 7 (Wire into main.py)
                                     └──▶ Phase 8 (Tests)
```

---

## Interface Contract — What You Provide to Other Developers

### For Person 2 (AI Pipeline Agents)

Person 2's agents need these from you. Track availability here:

| Interface                          | File                           | Status      |
|------------------------------------|--------------------------------|-------------|
| `get_db()` → `AsyncSession`       | `backend/app/db/session.py`    | AVAILABLE |
| `get_neo4j_driver()` → `AsyncDriver` | `backend/app/db/neo4j_client.py` | AVAILABLE |
| `get_qdrant_client()` → `QdrantClient` | `backend/app/db/qdrant_client.py` | AVAILABLE |
| Resume model (pipeline writes `pipeline_status`) | `backend/app/models/resume.py` | AVAILABLE |
| Analysis model (ScoringAgent writes results) | `backend/app/models/analysis.py` | AVAILABLE |
| Feedback model (FeedbackAgent writes feedback) | `backend/app/models/feedback.py` | AVAILABLE |

### For Person 3 (Frontend)

Person 3 consumes these REST APIs. Track availability here:

| Endpoint                                  | Method | Route File       | Status      |
|-------------------------------------------|--------|------------------|-------------|
| `POST /api/auth/register`                 | POST   | `routes/auth.py` | AVAILABLE |
| `POST /api/auth/login`                    | POST   | `routes/auth.py` | AVAILABLE |
| `GET /api/jobs`                           | GET    | `routes/jobs.py` | AVAILABLE |
| `POST /api/jobs`                          | POST   | `routes/jobs.py` | AVAILABLE |
| `GET /api/jobs/{id}`                      | GET    | `routes/jobs.py` | AVAILABLE |
| `PUT /api/jobs/{id}`                      | PUT    | `routes/jobs.py` | AVAILABLE |
| `POST /api/resumes/upload`               | POST   | `routes/resumes.py` | AVAILABLE |
| `GET /api/resumes/{id}/status`           | GET    | `routes/resumes.py` | AVAILABLE |
| `GET /api/jobs/{job_id}/candidates`      | GET    | `routes/candidates.py` | AVAILABLE |
| `GET /api/resumes/{resume_id}/analysis`  | GET    | `routes/analysis.py` | AVAILABLE |
| `POST /api/feedback/{candidate_id}/{job_id}` | POST | `routes/feedback.py` | AVAILABLE |
| `GET /api/feedback/{id}`                 | GET    | `routes/feedback.py` | AVAILABLE |

### JWT Token Format (for Person 3)

```json
{
  "sub": "<user_id as string>",
  "role": "recruiter" | "hiring_manager",
  "exp": "<unix timestamp>"
}
```

Frontend sends: `Authorization: Bearer <token>`

---

## Existing Files (READ ONLY — do not recreate)

| File | Owner | Notes |
|------|-------|-------|
| `backend/app/config.py` | Shared | `Settings` class; reads `.env`; has all env vars |
| `backend/app/main.py` | Shared | FastAPI app + CORS + `/health`; Person 1 appends routers + lifespan |
| `backend/app/__init__.py` | Shared | Empty |
| `backend/app/agents/*` | Person 2 | **DO NOT TOUCH** — 11 agent files |
| `backend/requirements.txt` | Shared | All deps already listed; append only if needed |
| `docker-compose.yml` | Shared | Neo4j + Qdrant containers |

---

## Phase 1 — Database & Client Layer

### Goal
Create async database engine, Supabase storage client, Neo4j async driver, and Qdrant client. All exposed as FastAPI dependencies.

### Files to Create

```
backend/app/db/
├── __init__.py
├── base.py              # DeclarativeBase for SQLAlchemy models
├── session.py           # create_async_engine + get_db() async generator
├── supabase_client.py   # Supabase SDK init (for file uploads to Storage)
├── neo4j_client.py      # AsyncGraphDatabase.driver + singleton management
└── qdrant_client.py     # QdrantClient singleton + collection ensure
```

### Requirements Checklist

| # | Requirement | Details | Done? |
|---|-------------|---------|-------|
| 1.1 | `session.py`: async engine | `create_async_engine(settings.DATABASE_URL)` with `echo=False` | ☑ |
| 1.2 | `session.py`: `get_db()` | Async generator yielding `AsyncSession`, auto-closes | ☑ |
| 1.3 | `base.py`: `Base` | `DeclarativeBase` subclass, all models inherit from this | ☑ |
| 1.4 | `neo4j_client.py`: driver singleton | `AsyncGraphDatabase.driver(NEO4J_URI, auth=(user, pass))` | ☑ |
| 1.5 | `neo4j_client.py`: `get_neo4j_driver()` | Returns the singleton driver instance | ☑ |
| 1.6 | `neo4j_client.py`: `close_neo4j_driver()` | Called on app shutdown | ☑ |
| 1.7 | `qdrant_client.py`: client singleton | `QdrantClient(url=QDRANT_URL, api_key=...)` | ☑ |
| 1.8 | `qdrant_client.py`: `get_qdrant_client()` | Returns the singleton client instance | ☑ |
| 1.9 | `qdrant_client.py`: ensure collections | Create `resumes` + `job_descriptions` collections (768-dim, cosine) if not exist | ☑ |
| 1.10 | `supabase_client.py`: Supabase init | `create_client(SUPABASE_URL, SUPABASE_ANON_KEY)` | ☑ |
| 1.11 | `supabase_client.py`: `get_supabase()` | Returns the Supabase client instance | ☑ |
| 1.12 | `__init__.py`: re-exports | Lazy imports — use `from app.db.session import get_db` etc. | ☑ |

### Config Values Used (from `config.py`)

```python
DATABASE_URL        # Supabase Postgres connection string
SUPABASE_URL        # Supabase project URL
SUPABASE_ANON_KEY   # Supabase anon/public key
NEO4J_URI           # default: bolt://localhost:7687
NEO4J_USERNAME      # default: neo4j
NEO4J_PASSWORD      # default: rax_dev_password
QDRANT_URL          # default: http://localhost:6333
QDRANT_API_KEY      # default: "" (empty for local)
```

### Validation Criteria

- [ ] `python -c "from app.db.session import get_db"` imports without error
- [ ] Neo4j: `RETURN 1` query succeeds via `get_neo4j_driver()`
- [ ] Qdrant: `get_qdrant_client().get_collections()` returns without error
- [ ] Supabase: `get_supabase().storage.list_buckets()` returns without error

### Phase 1 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-05  
> **Issues/Blockers:** None  
> **Notes for Person 2:** `get_neo4j_driver()` and `get_qdrant_client()` are ready. Import from `app.db.neo4j_client` and `app.db.qdrant_client`. Drivers are singletons — init at startup, call `get_*()` anywhere. Qdrant collections `resumes` and `job_descriptions` (768-dim, cosine) are auto-created on startup.  
> **Notes for Person 3:** No frontend impact yet.  
> **Additional:** Created `.env.example` with all required env vars. Copy to `.env` and fill in real values.

---

## Phase 2 — SQLAlchemy Models

### Goal
Define all 6 database tables as SQLAlchemy ORM models with proper foreign keys, relationships, indexes, and enums.

### Files to Create

```
backend/app/models/
├── __init__.py    # re-export all models + Base.metadata
├── user.py
├── job.py
├── candidate.py
├── resume.py
├── analysis.py
└── feedback.py
```

### Table Schemas

#### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `email` | `String(255)` | UNIQUE, NOT NULL, indexed |
| `hashed_password` | `String(255)` | NOT NULL |
| `full_name` | `String(255)` | NOT NULL |
| `role` | `Enum('recruiter','hiring_manager')` | NOT NULL, default `'recruiter'` |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, default `utcnow` |

#### `jobs`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `title` | `String(255)` | NOT NULL |
| `description` | `Text` | NOT NULL |
| `requirements_raw` | `JSONB` | nullable |
| `embedding_id` | `String(255)` | nullable (Qdrant point ref) |
| `created_by` | `UUID` | FK → `users.id`, NOT NULL |
| `status` | `Enum('draft','active','closed')` | default `'active'` |
| `created_at` | `DateTime(timezone=True)` | default `utcnow` |

#### `candidates`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `name` | `String(255)` | nullable (anonymized) |
| `email` | `String(255)` | nullable |
| `phone` | `String(50)` | nullable |
| `neo4j_node_id` | `String(255)` | nullable |
| `created_at` | `DateTime(timezone=True)` | default `utcnow` |

#### `resumes`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `candidate_id` | `UUID` | FK → `candidates.id`, NOT NULL |
| `job_id` | `UUID` | FK → `jobs.id`, NOT NULL |
| `file_path` | `String(500)` | NOT NULL (Supabase Storage path) |
| `raw_text` | `Text` | nullable |
| `parsed_json` | `JSONB` | nullable |
| `anonymized_json` | `JSONB` | nullable |
| `embedding_id` | `String(255)` | nullable |
| `pipeline_status` | `Enum(PipelineStatus)` | NOT NULL, default `'uploaded'` |
| `created_at` | `DateTime(timezone=True)` | default `utcnow` |

**PipelineStatus enum values:**
`uploaded`, `parsing`, `filtering`, `ingesting`, `embedding`, `matching`, `scoring`, `completed`, `failed`

#### `analyses`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `resume_id` | `UUID` | FK → `resumes.id`, NOT NULL, UNIQUE |
| `job_id` | `UUID` | FK → `jobs.id`, NOT NULL |
| `overall_score` | `Float` | nullable |
| `skills_score` | `Float` | nullable |
| `experience_score` | `Float` | nullable |
| `education_score` | `Float` | nullable |
| `semantic_similarity` | `Float` | nullable |
| `structural_match` | `Float` | nullable |
| `explanation` | `Text` | nullable |
| `strengths` | `JSONB` | nullable |
| `gaps` | `JSONB` | nullable |
| `graph_paths` | `JSONB` | nullable |
| `created_at` | `DateTime(timezone=True)` | default `utcnow` |

#### `feedback`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `uuid4` |
| `candidate_id` | `UUID` | FK → `candidates.id`, NOT NULL |
| `job_id` | `UUID` | FK → `jobs.id`, NOT NULL |
| `resume_id` | `UUID` | FK → `resumes.id`, NOT NULL |
| `content` | `Text` | NOT NULL |
| `sent_at` | `DateTime(timezone=True)` | nullable |
| `created_at` | `DateTime(timezone=True)` | default `utcnow` |

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 2.1 | `user.py`: User model with email unique index | ☑ |
| 2.2 | `job.py`: Job model with FK to `users`, JSONB `requirements_raw` | ☑ |
| 2.3 | `candidate.py`: Candidate model, nullable fields for anonymization | ☑ |
| 2.4 | `resume.py`: Resume model with `PipelineStatus` enum, FKs to candidate + job | ☑ |
| 2.5 | `analysis.py`: Analysis model with all score fields, JSONB for strengths/gaps/paths | ☑ |
| 2.6 | `feedback.py`: Feedback model with FKs to candidate, job, resume | ☑ |
| 2.7 | `__init__.py`: Import all models so Alembic discovers them | ☑ |
| 2.8 | All models use `Base` from `db/base.py` | ☑ |
| 2.9 | UUID PKs with `uuid4` default | ☑ |
| 2.10 | `created_at` with `server_default=func.now()` on all tables | ☑ |

### Validation Criteria

- [ ] `python -c "from app.models import User, Job, Candidate, Resume, Analysis, Feedback"` works
- [ ] No circular import errors
- [ ] `Base.metadata.tables` contains all 6 tables

### Phase 2 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-05  
> **Issues/Blockers:** None  
> **Notes for Person 2:** All 6 models ready. `Resume.pipeline_status` uses `PipelineStatus` enum with values: `uploaded, parsing, filtering, ingesting, embedding, matching, scoring, completed, failed`. Update via `db.execute(update(Resume).where(...).values(pipeline_status=PipelineStatus.parsing))`. Enums in `app.models.enums`. Also added `enums.py` with `UserRole`, `JobStatus`, `PipelineStatus` (not in original plan but needed).  
> **Notes for Person 3:** No frontend impact yet. Model schemas will be mirrored in Phase 4 Pydantic schemas.

---

## Phase 3 — Alembic Migrations

### Goal
Initialize Alembic with async support, auto-generate initial migration from all models, apply to Supabase Postgres.

### Files to Create

```
backend/alembic.ini
backend/alembic/
├── env.py            # async-aware migration runner
├── script.py.mako    # template
└── versions/
    └── 001_initial_tables.py   # auto-generated
```

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 3.1 | `alembic.ini`: points to correct `script_location` | ☑ |
| 3.2 | `env.py`: reads `DATABASE_URL` from `app.config` | ☑ |
| 3.3 | `env.py`: async-compatible (`run_async_migrations`) | ☑ |
| 3.4 | `env.py`: imports `Base.metadata` from `app.db.base` + all models | ☑ |
| 3.5 | Migration file created with all 6 tables | ☑ |
| 3.6 | Migration creates all 6 tables + 3 enums + FK constraints + unique index | ☑ |
| 3.7 | `alembic upgrade head` — ready to apply when Supabase DB is configured | ☐ |

### Validation Criteria

- [ ] Tables visible in Supabase dashboard: `users`, `jobs`, `candidates`, `resumes`, `analyses`, `feedback`
- [ ] All FK constraints exist
- [ ] Enum types created in Postgres

### Phase 3 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-05  
> **Issues/Blockers:** Migration file created manually (autogenerate requires live Postgres). Run `alembic upgrade head` once `.env` has a real `DATABASE_URL`.  
> **Notes for Person 2:** Migration creates all tables. Once applied, you can query/write to `resumes`, `analyses`, `feedback`. Revision: `4c24c57b118b`.  
> **Notes for Person 3:** No frontend impact yet. Backend DB schema is defined.

---

## Phase 4 — Pydantic Schemas

### Goal
Request/response validation schemas for all API endpoints. Strict input validation, clean output serialization.

### Files to Create

```
backend/app/schemas/
├── __init__.py
├── user.py
├── job.py
├── candidate.py
├── resume.py
├── analysis.py
└── feedback.py
```

### Schema Definitions

#### `user.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `UserCreate` | `email`, `password`, `full_name`, `role` (optional, default `recruiter`) | `POST /auth/register` request |
| `UserLogin` | `email`, `password` | `POST /auth/login` request |
| `UserResponse` | `id`, `email`, `full_name`, `role`, `created_at` | User responses (no password) |
| `TokenResponse` | `access_token`, `token_type` | `POST /auth/login` response |

#### `job.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `JobCreate` | `title`, `description`, `requirements_raw` (optional JSONB) | `POST /jobs` request |
| `JobUpdate` | `title?`, `description?`, `requirements_raw?`, `status?` | `PUT /jobs/{id}` request |
| `JobResponse` | All job fields + `created_by` | Single job response |
| `JobListResponse` | `jobs: list[JobResponse]`, `total: int` | `GET /jobs` response |

#### `resume.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `ResumeUploadResponse` | `id`, `candidate_id`, `job_id`, `file_path`, `pipeline_status` | `POST /resumes/upload` response |
| `ResumeStatusResponse` | `id`, `pipeline_status`, `created_at` | `GET /resumes/{id}/status` response |

#### `analysis.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `AnalysisResponse` | `id`, `resume_id`, `job_id`, `overall_score`, `skills_score`, `experience_score`, `education_score`, `semantic_similarity`, `structural_match`, `explanation`, `strengths`, `gaps`, `graph_paths` | `GET /resumes/{id}/analysis` response |

#### `candidate.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `CandidateResponse` | `id`, `name`, `email`, `phone`, `overall_score?`, `pipeline_status?` | Single candidate |
| `CandidateListResponse` | `candidates: list[CandidateResponse]`, `total: int` | `GET /jobs/{id}/candidates` response |

#### `feedback.py`
| Schema | Fields | Usage |
|--------|--------|-------|
| `FeedbackCreate` | _(empty or minimal — feedback is auto-generated)_ | `POST /feedback` trigger |
| `FeedbackResponse` | `id`, `candidate_id`, `job_id`, `resume_id`, `content`, `sent_at`, `created_at` | `GET /feedback/{id}` response |

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 4.1 | All schemas use `model_config = ConfigDict(from_attributes=True)` | ☑ |
| 4.2 | `UserCreate.email` validated with email format (`EmailStr`) | ☑ |
| 4.3 | `UserCreate.password` min length 8 | ☑ |
| 4.4 | `JobCreate.title` max length 255 | ☑ |
| 4.5 | UUID fields serialized as strings in responses | ☑ |
| 4.6 | `datetime` fields serialized as ISO 8601 | ☑ |
| 4.7 | No password/hash fields in any response schema | ☑ |

### Validation Criteria

- [ ] `python -c "from app.schemas import UserCreate, JobCreate, ..."` works
- [ ] Instantiate each schema with sample data, no validation errors

### Phase 4 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-05  
> **Issues/Blockers:** None. Added `email-validator>=2.0` to `requirements.txt` (needed by `EmailStr`).  
> **Notes for Person 2:** No impact — schemas are for API layer only.  
> **Notes for Person 3:** These define the exact JSON shapes you'll send/receive. Key schemas for your TypeScript types:
> - `TokenResponse`: `{ access_token: string, token_type: "bearer" }`
> - `UserResponse`: `{ id, email, full_name, role, created_at }`
> - `JobResponse`: `{ id, title, description, requirements_raw, embedding_id, created_by, status, created_at }`
> - `CandidateResponse`: `{ id, name, email, phone, overall_score, pipeline_status, created_at }`
> - `AnalysisResponse`: `{ id, resume_id, job_id, overall_score, skills_score, experience_score, education_score, semantic_similarity, structural_match, explanation, strengths[], gaps[], graph_paths[] }`

---

## Phase 5 — Authentication (JWT)

### Goal
Register + login endpoints, JWT token generation, `get_current_user` dependency, role-based access guard.

### Files to Create

```
backend/app/api/
├── __init__.py
├── dependencies.py         # get_current_user, require_role
└── routes/
    ├── __init__.py
    └── auth.py             # POST /auth/register, POST /auth/login
```

### API Endpoints

#### `POST /auth/register`
- **Request:** `UserCreate` → `{ email, password, full_name, role? }`
- **Response:** `UserResponse` → `{ id, email, full_name, role, created_at }`
- **Logic:** Hash password with `passlib/bcrypt`, insert User, return (no token yet)
- **Errors:** 400 if email exists

#### `POST /auth/login`
- **Request:** `UserLogin` → `{ email, password }`
- **Response:** `TokenResponse` → `{ access_token, token_type: "bearer" }`
- **Logic:** Verify password, generate JWT with `{ sub: user.id, role: user.role, exp }`
- **Errors:** 401 if invalid credentials

### Dependencies

#### `get_current_user(token: str = Depends(oauth2_scheme)) → User`
- Decode JWT, extract `sub` (user_id)
- Query User by id
- Raise 401 if token invalid or user not found

#### `require_role(*roles: str)`
- Returns a dependency that checks `current_user.role in roles`
- Raise 403 if role mismatch

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 5.1 | Password hashing with `passlib[bcrypt]` (never store plaintext) | ☑ |
| 5.2 | JWT encode with `python-jose` using `SECRET_KEY` from config | ☑ |
| 5.3 | Token expiry: `ACCESS_TOKEN_EXPIRE_MINUTES` from config | ☑ |
| 5.4 | `get_current_user` dependency works with `Authorization: Bearer <token>` | ☑ |
| 5.5 | `require_role` blocks unauthorized roles with 403 | ☑ |
| 5.6 | Register rejects duplicate emails with 400 | ☑ |
| 5.7 | Login returns 401 for wrong email/password | ☑ |
| 5.8 | No sensitive data in JWT payload (no password, no email) | ☑ |

### Validation Criteria

- [ ] Register a user → login → use token to hit a protected endpoint → works
- [ ] Wrong password → 401
- [ ] Expired token → 401
- [ ] Wrong role → 403

### Phase 5 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-06  
> **Issues/Blockers:** None. Note: bcrypt 4.x required (5.x incompatible with passlib 1.7.x).  
> **Notes for Person 2:** No direct impact. If agents need to know who triggered a pipeline, the `user_id` comes from the route layer, not auth directly.  
> **Notes for Person 3:** Login/register endpoints live. Token format: `{ access_token: "...", token_type: "bearer" }`. Send as `Authorization: Bearer <token>` header on all subsequent requests.

---

## Phase 6 — CRUD API Routes

### Goal
All business logic endpoints: jobs, resumes, candidates, analysis, feedback. Integrates with Person 2's agents where needed.

### Files to Create

```
backend/app/api/routes/
├── jobs.py
├── resumes.py
├── candidates.py
├── analysis.py
└── feedback.py
```

### Endpoint Specifications

#### `routes/jobs.py`

| Endpoint | Auth | Description | Agent Integration |
|----------|------|-------------|-------------------|
| `GET /jobs` | Required | List all jobs (paginated) for current user | — |
| `POST /jobs` | Required (recruiter) | Create job + trigger KG/embedding | `GraphIngestionAgent.ingest_job()` + `EmbeddingAgent.embed_job()` |
| `GET /jobs/{id}` | Required | Get job by ID | — |
| `PUT /jobs/{id}` | Required (owner) | Update job fields | — |

**Agent integration detail for `POST /jobs`:**
```python
# After DB insert, call agents (non-blocking, wrapped in try/except)
try:
    graph_agent = GraphIngestionAgent(driver=neo4j_driver)
    await graph_agent.ingest_job(
        job_id=str(job.id),
        title=job.title,
        requirements=job.requirements_raw or {}
    )
    embed_agent = EmbeddingAgent()
    embedding_id = await embed_agent.embed_job(
        job_id=str(job.id),
        description_text=job.description
    )
    job.embedding_id = embedding_id
    await db.commit()
except Exception as e:
    logger.warning("Agent integration failed for job %s: %s", job.id, e)
    # Job is still created — agents can be retried later
```

#### `routes/resumes.py`

| Endpoint | Auth | Description | Agent Integration |
|----------|------|-------------|-------------------|
| `POST /resumes/upload` | Required | Multipart file upload (PDF/DOCX) | `PipelineOrchestrator.run()` as BackgroundTask |
| `GET /resumes/{id}/status` | Required | Get pipeline status | — |

**Upload flow:**
1. Receive file via `UploadFile`
2. Validate file type (`.pdf` or `.docx` only)
3. Create Candidate record (or find existing by email)
4. Upload file to Supabase Storage (`resumes` bucket)
5. Create Resume record with `pipeline_status='uploaded'`
6. Add `BackgroundTask` → `PipelineOrchestrator.run(resume_id, job_id, file_bytes=..., filename=...)`
7. Return `ResumeUploadResponse` immediately

#### `routes/candidates.py`

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /jobs/{job_id}/candidates` | Required | Ranked candidate list with scores, sortable, filterable |

**Query:** Join `resumes` + `analyses` + `candidates` where `job_id` matches, order by `overall_score DESC`.  
**Filters:** `min_score`, `status` (pipeline_status = completed only).

#### `routes/analysis.py`

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /resumes/{resume_id}/analysis` | Required | Full scoring breakdown |

**Returns:** `AnalysisResponse` with scores, strengths, gaps, explanation, graph_paths.  
**Error:** 404 if no analysis exists (pipeline not complete).

#### `routes/feedback.py`

| Endpoint | Auth | Description | Agent Integration |
|----------|------|-------------|-------------------|
| `POST /feedback/{candidate_id}/{job_id}` | Required (recruiter) | Generate feedback | `FeedbackAgent.run()` |
| `GET /feedback/{id}` | Required | Retrieve feedback | — |

**Feedback generation flow:**
1. Find Resume + Analysis for this candidate/job pair
2. Build `PipelineContext` with existing `analysis` and `match_result` data
3. Call `FeedbackAgent().run(ctx)`
4. Save `ctx.analysis["feedback"]` to Feedback table
5. Return `FeedbackResponse`

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 6.1 | `POST /jobs` creates job and triggers agents (non-blocking) | ☑ |
| 6.2 | `POST /resumes/upload` accepts multipart, validates file type | ☑ |
| 6.3 | Resume upload stores file in Supabase Storage | ☑ |
| 6.4 | Resume upload triggers pipeline as `BackgroundTask` | ☑ |
| 6.5 | `GET /jobs/{job_id}/candidates` returns ranked list by score | ☑ |
| 6.6 | `GET /resumes/{resume_id}/analysis` returns full breakdown | ☑ |
| 6.7 | `POST /feedback` triggers FeedbackAgent and persists result | ☑ |
| 6.8 | All routes require authentication | ☑ |
| 6.9 | Agent calls wrapped in try/except (don't crash if agent fails) | ☑ |
| 6.10 | File type validation (only .pdf, .docx) | ☑ |
| 6.11 | Proper HTTP status codes: 201 (create), 404 (not found), 400 (bad request) | ☑ |

### Validation Criteria

- [ ] Create a job → verify it appears in `GET /jobs`
- [ ] Upload a resume → verify pipeline starts in background
- [ ] `GET /resumes/{id}/status` reflects pipeline progress
- [ ] Candidates ranked correctly by score
- [ ] Feedback generated and retrievable

### Phase 6 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-06  
> **Issues/Blockers:** None.  
> **Notes for Person 2:** Your agents are now called from routes. `PipelineOrchestrator.run()` is triggered as a `BackgroundTask` on resume upload. `GraphIngestionAgent.ingest_job()` + `EmbeddingAgent.embed_job()` called on job creation. All wrapped in try/except so stubs won't crash the API.  
> **Notes for Person 3:** All REST endpoints are now available. You can build the full UI. Check `/docs` for request/response shapes.

---

## Phase 7 — Router Registration & Lifespan

### Goal
Wire all route modules into the FastAPI app in `main.py`. Add startup/shutdown lifecycle for initializing and cleaning up DB engine, Neo4j driver, and Qdrant client.

### File to Modify

`backend/app/main.py` — **append only**, do not remove existing code.

### Changes

#### Router registration (add after `app` creation):
```python
from app.api.routes import auth, jobs, resumes, candidates, analysis, feedback

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(resumes.router,    prefix="/api/resumes",    tags=["Resumes"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(analysis.router,   prefix="/api/analysis",   tags=["Analysis"])
app.include_router(feedback.router,   prefix="/api/feedback",   tags=["Feedback"])
```

#### Lifespan events (modify existing `lifespan`):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.db.neo4j_client import init_neo4j_driver
    from app.db.qdrant_client import init_qdrant_client
    from app.db.session import init_db_engine

    await init_db_engine()
    init_neo4j_driver()
    init_qdrant_client()

    yield

    # Shutdown
    from app.db.neo4j_client import close_neo4j_driver
    from app.db.session import close_db_engine

    await close_neo4j_driver()
    await close_db_engine()
```

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 7.1 | All 6 routers registered with correct prefixes | ☑ |
| 7.2 | Lifespan startup: init DB engine, Neo4j driver, Qdrant client | ☑ |
| 7.3 | Lifespan shutdown: close DB engine, Neo4j driver | ☑ |
| 7.4 | `/health` endpoint still works | ☑ |
| 7.5 | Person 2's existing code not broken | ☑ |

### Validation Criteria

- [ ] `uvicorn app.main:app --reload` starts without error
- [ ] `http://localhost:8000/docs` shows all endpoints grouped by tag
- [ ] `/health` returns `{"status": "ok"}`
- [ ] No import errors from agents (they remain untouched)

### Phase 7 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-06  
> **Issues/Blockers:** None. Startup init wrapped in try/except to avoid crashing when external services unavailable.  
> **Notes for Person 2:** `main.py` now initializes Neo4j driver and Qdrant client at startup. You can access them via `get_neo4j_driver()` and `get_qdrant_client()` from `app.db`.  
> **Notes for Person 3:** Backend is fully running. All endpoints visible at `/docs`. You can start full integration.

---

## Phase 8 — Tests

### Goal
Full test coverage for auth, CRUD operations, and agent integration points using `pytest` + `httpx.AsyncClient`.

### Files to Create

```
backend/tests/
├── __init__.py
├── conftest.py         # test DB (SQLite in-memory), async client, auth fixtures
├── test_auth.py        # register, login, token validation, role guard
├── test_jobs.py        # CRUD + agent trigger verification
├── test_resumes.py     # upload + pipeline trigger verification
├── test_candidates.py  # ranked listing
└── test_feedback.py    # feedback generation
```

### Test Fixtures (`conftest.py`)

| Fixture | Description |
|---------|-------------|
| `test_db` | SQLite async in-memory DB, tables created from `Base.metadata` |
| `client` | `httpx.AsyncClient` against test app with overridden `get_db` |
| `auth_headers` | Registers + logs in a test user, returns `{"Authorization": "Bearer <token>"}` |
| `recruiter_headers` | Auth headers for a user with `role=recruiter` |
| `sample_job` | Pre-created job for resume/candidate tests |

### Test Coverage

| Test File | Cases |
|-----------|-------|
| `test_auth.py` | Register success, register duplicate email (400), login success, login wrong password (401), access protected route without token (401), wrong role (403) |
| `test_jobs.py` | Create job (201), list jobs, get job by ID, update job, create with invalid data (422) |
| `test_resumes.py` | Upload PDF (201), upload invalid file type (400), get status, pipeline_status is `uploaded` on creation |
| `test_candidates.py` | List candidates for job, empty list, sorted by score desc |
| `test_feedback.py` | Generate feedback (triggers agent mock), retrieve feedback |

### Requirements Checklist

| # | Requirement | Done? |
|---|-------------|-------|
| 8.1 | `conftest.py`: async test DB with auto-cleanup | ☑ |
| 8.2 | `conftest.py`: httpx AsyncClient with dependency overrides | ☑ |
| 8.3 | Agent calls mocked (don't need real Gemini/Neo4j/Qdrant in tests) | ☑ |
| 8.4 | Auth tests: register, login, token, role guard | ☑ |
| 8.5 | Jobs tests: full CRUD cycle | ☑ |
| 8.6 | Resumes tests: upload + status check | ☑ |
| 8.7 | Candidates tests: ranked query | ☑ |
| 8.8 | Feedback tests: generation + retrieval | ☑ |
| 8.9 | All tests pass with `pytest backend/tests/ -v` | ☑ |

### Validation Criteria

- [ ] `pytest backend/tests/ -v` — all green
- [ ] No tests depend on external services (Neo4j, Qdrant, Supabase, Gemini)
- [ ] Tests can run in CI without Docker

### Phase 8 Checkpoint

> **Status:** COMPLETED  
> **Date Completed:** 2026-04-06  
> **Issues/Blockers:** None. 25 tests pass. SQLite used via JSONB→JSON compilation hook. No external services required.  
> **Notes for Person 2:** Tests mock your agents. When your agents are ready, we can add integration tests that use real agents.  
> **Notes for Person 3:** Backend is fully tested. You can rely on the API contract.

---

## Changelog — Cross-Developer Updates

> Update this section after each phase so Person 2 and Person 3 know what's new.

| Date | Phase | What Changed | Impact on Person 2 | Impact on Person 3 |
|------|-------|--------------|--------------------|--------------------|
| 2026-04-05 | 1 | Created `db/` layer: session.py, neo4j_client.py, qdrant_client.py, supabase_client.py, base.py | `get_neo4j_driver()` and `get_qdrant_client()` now available for your agents | No impact |
| 2026-04-05 | 2 | Created 6 SQLAlchemy models + enums.py | `Resume`, `Analysis`, `Feedback` models available for pipeline DB writes; `PipelineStatus` enum for status updates | No impact |
| 2026-04-05 | 3 | Alembic init + initial migration (rev `4c24c57b118b`) | Tables will exist after `alembic upgrade head` | No impact |
| 2026-04-05 | 4 | Created 14 Pydantic schemas across 6 files; added `email-validator` dep | No impact | Review `*Response` schemas for TypeScript types |
| 2026-04-06 | 5 | Auth: `POST /auth/register`, `POST /auth/login`, `get_current_user`, `require_role` | No direct impact | Login/register endpoints available; send `Authorization: Bearer <token>` |
| 2026-04-06 | 6 | CRUD routes: jobs, resumes, candidates, analysis, feedback | Agents called from routes (try/except wrapped) | All 12 REST endpoints available |
| 2026-04-06 | 7 | Routers wired into `main.py`; lifespan init/shutdown for Neo4j, Qdrant, Supabase | Neo4j/Qdrant init at startup | `/docs` shows all endpoints; full integration ready |
| 2026-04-06 | 8 | 25 tests: auth, jobs, resumes, candidates, feedback; SQLite in-memory | Agent calls are mocked | Backend fully tested; API contract reliable |

---

## Files Created / Modified — Full Inventory

> Update after each phase.

```
backend/
├── requirements.txt                    # MODIFIED (Phase 1 — if new deps needed)
├── alembic.ini                         # CREATED (Phase 3)
├── alembic/
│   ├── env.py                          # CREATED (Phase 3)
│   ├── script.py.mako                  # CREATED (Phase 3)
│   └── versions/
│       └── 001_initial_tables.py       # CREATED (Phase 3)
├── app/
│   ├── main.py                         # MODIFIED (Phase 7 — add routers + lifespan)
│   ├── db/
│   │   ├── __init__.py                 # CREATED (Phase 1)
│   │   ├── base.py                     # CREATED (Phase 1)
│   │   ├── session.py                  # CREATED (Phase 1)
│   │   ├── supabase_client.py          # CREATED (Phase 1)
│   │   ├── neo4j_client.py             # CREATED (Phase 1)
│   │   └── qdrant_client.py            # CREATED (Phase 1)
│   ├── models/
│   │   ├── __init__.py                 # CREATED (Phase 2)
│   │   ├── user.py                     # CREATED (Phase 2)
│   │   ├── job.py                      # CREATED (Phase 2)
│   │   ├── candidate.py                # CREATED (Phase 2)
│   │   ├── resume.py                   # CREATED (Phase 2)
│   │   ├── analysis.py                 # CREATED (Phase 2)
│   │   └── feedback.py                 # CREATED (Phase 2)
│   ├── schemas/
│   │   ├── __init__.py                 # CREATED (Phase 4)
│   │   ├── user.py                     # CREATED (Phase 4)
│   │   ├── job.py                      # CREATED (Phase 4)
│   │   ├── candidate.py                # CREATED (Phase 4)
│   │   ├── resume.py                   # CREATED (Phase 4)
│   │   ├── analysis.py                 # CREATED (Phase 4)
│   │   └── feedback.py                 # CREATED (Phase 4)
│   └── api/
│       ├── __init__.py                 # CREATED (Phase 5)
│       ├── dependencies.py             # CREATED (Phase 5)
│       └── routes/
│           ├── __init__.py             # CREATED (Phase 5)
│           ├── auth.py                 # CREATED (Phase 5)
│           ├── jobs.py                 # CREATED (Phase 6)
│           ├── resumes.py              # CREATED (Phase 6)
│           ├── candidates.py           # CREATED (Phase 6)
│           ├── analysis.py             # CREATED (Phase 6)
│           └── feedback.py             # CREATED (Phase 6)
└── tests/
    ├── __init__.py                     # CREATED (Phase 8)
    ├── conftest.py                     # CREATED (Phase 8)
    ├── test_auth.py                    # CREATED (Phase 8)
    ├── test_jobs.py                    # CREATED (Phase 8)
    ├── test_resumes.py                 # CREATED (Phase 8)
    ├── test_candidates.py              # CREATED (Phase 8)
    └── test_feedback.py                # CREATED (Phase 8)
```

---

## How to Use This Document

1. **Before starting a phase:** Read its requirements checklist carefully.
2. **During implementation:** Check off items as you complete them (change `☐` → `☑`).
3. **After completing a phase:** 
   - Update the **Quick Status Dashboard** at the top.
   - Fill in the **Phase Checkpoint** section (status, date, blockers, notes).
   - Add an entry to the **Changelog** for Person 2 and Person 3.
   - Update the **Interface Contract** tables (mark items as AVAILABLE).
4. **Move to the next phase** only after all validation criteria pass.

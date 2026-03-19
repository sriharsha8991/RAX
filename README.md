# RAX — Resume Analysis eXpert

An AI-powered hiring platform that uses semantic understanding and explainable AI to screen, evaluate, and shortlist candidates — replacing keyword-based ATS filtering with a fair, transparent, and distributed multi-agent pipeline powered by a hybrid knowledge graph + vector search architecture.

---

## Team

| Member | Role | Owns |
|---|---|---|
| **Person 1** | Backend Core | FastAPI, Supabase, Auth, DB models, CRUD APIs, Neo4j/Qdrant client setup |
| **Person 2** | AI Pipeline | Gemini agents, Neo4j graph ingestion, Qdrant embedding, hybrid matching, WebSocket |
| **Person 3** | Frontend | React + TypeScript, real-time UI, dashboards, candidate views, feedback |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React.js + TypeScript (Vite) | SPA with real-time WebSocket support |
| UI Framework | Tailwind CSS + shadcn/ui | Accessible, responsive components |
| State Management | Zustand | Lightweight client-side state |
| Backend | Python FastAPI | Async REST API + WebSocket server |
| Auth | JWT (python-jose + passlib) | Stateless role-based authentication |
| Database | Supabase (PostgreSQL) | Relational data — users, jobs, candidates, scores |
| File Storage | Supabase Storage | Resume PDF/DOCX file storage |
| Knowledge Graph | Neo4j (AuraDB / Docker) | Structural reasoning, skill taxonomy, explainable matching |
| Vector Store | Qdrant | Semantic similarity search on embeddings |
| AI / LLM | Google Gemini (`gemini-1.5-pro`) | Resume parsing, scoring, feedback generation |
| Embeddings | Gemini `text-embedding-004` | 768-dim vector representations |
| Real-Time | WebSocket (FastAPI native) | Live pipeline status updates |
| Migrations | Alembic | Database schema versioning |
| Deployment | Vercel / Railway / Neo4j AuraDB / Qdrant Cloud / Supabase | All free-tier cloud |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT TIER                        │
│  React + TypeScript (Vite) + Tailwind + shadcn/ui   │
│  Zustand state │ Axios REST │ WebSocket live updates │
│  Deployed on: Vercel                                 │
└──────────────────────┬──────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────┼──────────────────────────────┐
│                  SERVER TIER                         │
│  Python FastAPI (async)                              │
│  ┌────────────────────────────────────────────────┐  │
│  │ Pipeline Orchestrator                          │  │
│  │ ResumeParser → BiasFilter → [GraphIngestion    │  │
│  │                              ║ Embedding]      │  │
│  │                            → HybridMatch       │  │
│  │                            → Scoring           │  │
│  │ FeedbackAgent (on demand)                      │  │
│  └────────────────────────────────────────────────┘  │
│  JWT Auth │ Alembic Migrations │ Background Tasks    │
│  Deployed on: Railway / Render                       │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
┌───────┼──────┐ ┌─────┼──────┐ ┌────┼──────┐ ┌──────────────┐
│  DATA TIER   │ │ GRAPH TIER │ │VECTOR TIER│ │   AI TIER    │
│              │ │            │ │           │ │              │
│  Supabase    │ │ Neo4j      │ │ Qdrant    │ │ Google       │
│  (PostgreSQL)│ │ Knowledge  │ │ Vector DB │ │ Gemini       │
│  + Storage   │ │ Graph      │ │           │ │              │
│              │ │            │ │ resumes   │ │ gemini-1.5   │
│  Users       │ │ Candidate  │ │ job_descs │ │ -pro         │
│  Jobs        │ │ Skill      │ │           │ │              │
│  Resumes     │ │ Company    │ │ Cosine    │ │ text-embed   │
│  Analyses    │ │ Role       │ │ Similarity│ │ -004 (768d)  │
│  Feedback    │ │ Education  │ │           │ │              │
└──────────────┘ │ SkillClstr │ └───────────┘ └──────────────┘
                 │ IS_SIMILAR │
                 │ HAS_SKILL  │
                 │ REQUIRES   │
                 └────────────┘
```

---

## Hybrid Scoring System

RAX uses **multi-dimensional scoring** instead of a single similarity number. Each candidate is evaluated across four weighted components:

```
Final Score = 0.50 × Structural Skill Match  (Neo4j Knowledge Graph)
            + 0.30 × Semantic Similarity      (Qdrant Vector Search)
            + 0.15 × Experience Match          (Neo4j Knowledge Graph)
            + 0.05 × Education Match           (Neo4j Knowledge Graph)
```

| Dimension | Weight | Source | What It Measures |
|---|---|---|---|
| **Structural Skill Match** | 50% | Neo4j | Direct + similar skill matches via graph traversal; partial credit through `IS_SIMILAR_TO` edges |
| **Semantic Similarity** | 30% | Qdrant | Cosine similarity between resume and JD embeddings; catches vocabulary mismatch |
| **Experience Match** | 15% | Neo4j | Years-per-skill comparison against job requirements |
| **Education Match** | 5% | Neo4j | Degree level comparison (High School=1 → PhD=5) |

**Why these weights:**
- **Structural (50%)** — Most reliable, most explainable signal; directly verifiable through graph paths
- **Semantic (30%)** — Safety net when graph is sparse; captures career direction and domain alignment
- **Experience (15%)** — Refinement signal, not a primary filter; avoids penalizing inflated JD requirements
- **Education (5%)** — Weakest predictor of job performance; tiebreaker, not gatekeeper

Weights are **configurable per job posting**. If the graph is sparse (poorly parsed resume), vector score naturally compensates.

---

## Knowledge Graph Schema (Neo4j)

### Node Types

| Node | Description | Created By |
|---|---|---|
| `Candidate` | Job applicant | GraphIngestionAgent |
| `Job` | Job posting | Job creation API |
| `Skill` | Technical or soft skill | GraphIngestionAgent |
| `SkillCluster` | Skill category group | GraphIngestionAgent |
| `Company` | Company candidate worked at | GraphIngestionAgent |
| `Role` | Job title held | GraphIngestionAgent |
| `Education` | Degree type | GraphIngestionAgent |
| `Institution` | University/school (anonymized before scoring) | GraphIngestionAgent |

### Relationships Checked During Scoring

| Relationship | Direction | Properties | Scoring Impact |
|---|---|---|---|
| `HAS_SKILL` | Candidate → Skill | `years`, `proficiency` | Structural (50%) + Experience (15%) |
| `REQUIRES_SKILL` | Job → Skill | `priority`, `min_years` | Structural (50%) + Experience (15%) |
| `IS_SIMILAR_TO` | Skill → Skill | `score` (0–1) | Partial credit in Structural (50%) |
| `BELONGS_TO` | Skill → SkillCluster | — | Hierarchical group matching |
| `WORKED_AT` | Candidate → Company | `duration`, `start`, `end` | Experience (15%) |
| `HELD_ROLE` | Candidate → Role | `title` | Seniority alignment |
| `HAS_DEGREE` | Candidate → Education | `level`, `field` | Education (5%) |
| `REQUIRES_DEGREE` | Job → Education | `min_level` | Education (5%) |
| `STUDIED_AT` | Candidate → Institution | — | **Excluded from scoring** (bias prevention) |

### Self-Enriching Graph

The knowledge graph grows with every resume processed:
1. New resumes create `Skill` nodes and `HAS_SKILL` edges
2. `EmbeddingAgent` checks Qdrant for skill vector proximity
3. If two skills have cosine similarity > 0.7 but no `IS_SIMILAR_TO` edge → auto-created in Neo4j
4. Future candidates benefit from richer partial credit paths

---

## AI Pipeline (Multi-Agent)

```
Resume Upload (PDF/DOCX)
        │
        ▼
┌───────────────────┐
│ ResumeParserAgent │  Extract text → Gemini → structured JSON
└────────┬──────────┘
         ▼
┌───────────────────┐
│ BiasFilterAgent   │  Anonymize name, gender, institution → [UNIVERSITY]
└────────┬──────────┘
         │
   ┌─────┴──────┐        (parallel execution)
   ▼             ▼
┌──────────┐ ┌──────────┐
│ Graph    │ │ Embedding│
│ Ingestion│ │ Agent    │
│ → Neo4j  │ │ → Qdrant │
└────┬─────┘ └────┬─────┘
     └──────┬─────┘
            ▼
┌───────────────────────┐
│ HybridMatchingAgent   │  Neo4j graph traversal + Qdrant cosine similarity
└────────┬──────────────┘  → fused weighted score
         ▼
┌───────────────────┐
│ ScoringAgent      │  Gemini + hybrid context → multi-dim scores + explanation
└────────┬──────────┘
         ▼
   Stored in DB + pushed via WebSocket

┌───────────────────┐
│ FeedbackAgent     │  On-demand: AI-generated constructive rejection feedback
└───────────────────┘
```

---

## Repository Structure

```
repo-dev1/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml          # local dev: Neo4j + Qdrant (Supabase is cloud-hosted)
├── docs/
│   ├── initial_doc.md
│   ├── stage2_design_document.md
│   ├── stage2_doc_requirment.md
│   ├── stage2_ppt_detailed.md
│   ├── stage2_ppt_short.md
│   ├── scoring_and_kg_relationships.md
│   └── architecture_eraserio.md
├── frontend/                   # React + TypeScript (Person 3)
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── store/
│   ├── vercel.json
│   └── vite.config.ts
└── backend/                    # Python FastAPI (Person 1 + Person 2)
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── db/
    │   │   ├── session.py          # SQLAlchemy async (Supabase Postgres)
    │   │   ├── base.py
    │   │   ├── supabase_client.py
    │   │   ├── neo4j_client.py     # Neo4j async driver + session factory
    │   │   └── qdrant_client.py    # Qdrant client init + collection setup
    │   ├── models/
    │   ├── schemas/
    │   ├── api/
    │   │   └── routes/
    │   └── agents/             # AI pipeline (Person 2)
    │       ├── pipeline_context.py
    │       ├── base_agent.py
    │       ├── resume_parser_agent.py
    │       ├── bias_filter_agent.py
    │       ├── graph_ingestion_agent.py   # Neo4j graph decomposition
    │       ├── embedding_agent.py         # Qdrant vector embedding
    │       ├── hybrid_matching_agent.py   # Fuses Neo4j + Qdrant signals
    │       ├── scoring_agent.py
    │       ├── feedback_agent.py
    │       └── orchestrator.py
    ├── alembic/
    ├── tests/
    ├── Dockerfile
    └── requirements.txt
```

---

## Local Development Setup

### Prerequisites
- Docker + Docker Compose
- Node.js 20+
- Python 3.11+
- A Google Gemini API key
- A [Supabase](https://supabase.com) account (free tier) — provides `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- Neo4j AuraDB (free tier) or local Neo4j via Docker
- Qdrant Cloud (free 1 GB) or local Qdrant via Docker

### 1. Clone & configure env

```bash
git clone <repo-url>
cd repo-dev1
cp .env.example .env
# Fill in: GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY, DATABASE_URL,
#          NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, QDRANT_URL, QDRANT_API_KEY, SECRET_KEY
```

### 2. Start local services

```bash
docker-compose up -d   # starts Neo4j + Qdrant locally (Supabase DB is cloud-hosted)
```

### 3. Run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows  (source .venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Implementation Plan (3-Person, 6 Weeks)

### Phase 0 — Project Scaffolding (All 3 members · Week 1)
- Finalize README, `.env.example`, `.gitignore`
- Docker Compose with `neo4j:5-community` + `qdrant/qdrant` (named volumes + health checks)
- Create Supabase project; copy connection string + keys into `.env`
- Create Neo4j AuraDB free instance or verify local Docker works

---

### Person 1 — Backend Core (FastAPI + Supabase + Auth)

**Owns:** `backend/app/db/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/api/routes/`, `backend/alembic/`

#### Phase 1 — Backend Core (Weeks 2–3)

**Step 1 — Project Bootstrap**
- Create `backend/` with `requirements.txt`:
  `fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `alembic`, `asyncpg`, `psycopg2-binary`, `supabase`, `python-dotenv`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`
- `backend/app/main.py` — FastAPI instance, CORS middleware, router inclusion, lifespan handler (DB init, Neo4j driver init, Qdrant collection init)
- `backend/app/config.py` — Pydantic `Settings` class reading from env vars

**Step 2 — Database Layer**
- `session.py` — SQLAlchemy async engine pointing at Supabase Postgres URI (`?sslmode=require`)
- `base.py` — declarative base
- `supabase_client.py` — Supabase Python client for file storage
- `neo4j_client.py` — Neo4j async driver init + session factory
- `qdrant_client.py` — Qdrant client init + collection creation (`resumes`, `job_descriptions`)
- `alembic/` — async-aware config against Supabase

**Step 3 — SQLAlchemy Models**

| Model | Key Fields |
|---|---|
| `user.py` | `id`, `email`, `hashed_password`, `role` (recruiter \| hiring_manager), `created_at` |
| `job.py` | `id`, `title`, `description`, `requirements_raw`, `embedding_id`, `created_by`, `status` |
| `candidate.py` | `id`, `name` (nullable), `email`, `created_at` |
| `resume.py` | `id`, `candidate_id`, `job_id`, `file_path`, `raw_text`, `parsed_json` (JSONB), `embedding_id`, `status` |
| `analysis.py` | `id`, `resume_id`, `overall_score`, `skills_score`, `experience_score`, `education_score`, `explanation`, `strengths` (JSONB), `gaps` (JSONB) |
| `feedback.py` | `id`, `candidate_id`, `job_id`, `content`, `sent_at` |

**Step 4 — Pydantic Schemas** — Request/response schemas with field validation

**Step 5 — Auth**
- `POST /auth/register`, `POST /auth/login` (returns JWT)
- `get_current_user` dependency (JWT decode)

**Step 6 — API Routes**
- `jobs.py` — CRUD; on create → fires JD embedding + graph ingestion (calls Person 2's agents)
- `resumes.py` — bulk upload; stores file; triggers `PipelineOrchestrator` as `BackgroundTask`
- `candidates.py` — ranked list by score for a job; filter/sort
- `analysis.py` — full analysis detail for a resume
- `feedback.py` — trigger `FeedbackAgent` and retrieve result

**Step 7 — Alembic Migration** — Generate + apply against Supabase Postgres

**Step 8 — Unit Tests** — `httpx.AsyncClient` + mocked DB; test auth + route guards

---

### Person 2 — AI Pipeline (Gemini + Neo4j + Qdrant + WebSocket)

**Owns:** `backend/app/agents/`, `backend/app/api/routes/ws.py`

**Additional deps:** `google-generativeai`, `neo4j`, `qdrant-client`, `pypdf2`, `python-docx`

#### Phase 2 — Multi-Agent Pipeline (Weeks 2–4)

All agents share a `PipelineContext` dataclass. Each agent: `async def run(ctx: PipelineContext) -> PipelineContext`

**Step 1 — Foundation**
- `pipeline_context.py` — `resume_id`, `job_id`, `raw_text`, `parsed_resume`, `filtered_resume`, `graph_node_id`, `qdrant_point_id`, `match_result`, `analysis`
- `base_agent.py` — abstract `BaseAgent`; shared Gemini client init

**Step 2 — ResumeParserAgent**
- Extract raw text from PDF (PyPDF2) / DOCX (python-docx)
- Gemini prompt → structured JSON: `{ skills, experience[], education[], name, email, phone }`

**Step 3 — BiasFilterAgent**
- Anonymize: name → `[CANDIDATE_ID]`, institutions → `[UNIVERSITY]`, gender/nationality signals removed
- Runs BEFORE any scoring

**Step 4 — GraphIngestionAgent**
- Decompose resume into Neo4j nodes: `Candidate`, `Skill`, `Company`, `Role`, `Education`, `Institution`
- Create relationships: `HAS_SKILL`, `WORKED_AT`, `HELD_ROLE`, `STUDIED_AT`, `HAS_DEGREE` with properties
- Normalize skill names via Gemini; classify into `SkillCluster` nodes
- `MERGE` for idempotency
- Also handles JD ingestion: `REQUIRES_SKILL`, `REQUIRES_DEGREE`

**Step 5 — EmbeddingAgent** (parallel with Step 4)
- Embed resume text using Gemini `text-embedding-004` (768-dim)
- Upsert into Qdrant `resumes` + `job_descriptions` collections

**Step 6 — HybridMatchingAgent**
- Neo4j Cypher: direct skill matches, `IS_SIMILAR_TO` partial credit, experience depth, education fit
- Qdrant: cosine similarity resume ↔ JD
- Score fusion: `0.50 × structural + 0.30 × semantic + 0.15 × experience + 0.05 × education`
- Auto-enrichment: if Qdrant finds high similarity between two skills with no Neo4j edge → create `IS_SIMILAR_TO`

**Step 7 — ScoringAgent**
- Gemini prompt with hybrid context → `{ overall_score, skills_score, experience_score, education_score, strengths[], gaps[], explanation }`
- Persist to `analyses` table

**Step 8 — FeedbackAgent** (on-demand, not in main pipeline)
- Gemini prompt → 150–200 word constructive feedback referencing specific graph matches/gaps

**Step 9 — PipelineOrchestrator**
- Runs: `ResumeParser → BiasFilter → [GraphIngestion ║ Embedding] → HybridMatching → Scoring`
- Updates `resume.status` per stage
- Publishes WebSocket events after each agent

#### Phase 3 — Real-Time WebSocket (Week 4)

**Step 10 — WebSocket Route**
- `WS /ws/pipeline/{job_id}`
- In-memory pub/sub; events: `{ resume_id, stage, status, score? }`
- Stages: `parsing → filtering → graph_ingestion → embedding → hybrid_matching → scoring → completed`

**Step 11 — Unit Tests** — Mock Gemini, Neo4j, Qdrant; test each agent's I/O contract

---

### Person 3 — Frontend (React + TypeScript + Vite)

**Owns:** `frontend/`

**Key packages:** `react-router-dom`, `axios`, `zustand`, `react-hook-form`, `zod`, `tailwindcss`, `shadcn/ui`, `react-dropzone`, `recharts`

#### Phase 4 — Frontend (Weeks 2–5)

**Step 1 — Scaffold**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install react-router-dom axios zustand react-hook-form zod react-dropzone recharts
npx tailwindcss init && npx shadcn-ui@latest init
```

**Step 2 — Auth Store & Service**
- Zustand store: `{ token, user, login(), logout() }`
- Axios instance with JWT header interceptor
- Protected route wrapper

**Step 3 — Auth Pages**
- `LoginPage.tsx` — email/password (react-hook-form + zod)
- `RegisterPage.tsx` — email, password, role selector

**Step 4 — App Shell**
- Sidebar nav: Dashboard, Jobs, Candidates, Settings
- `ProtectedRoute.tsx` redirect guard

**Step 5 — Dashboard**
- Summary cards: active jobs, resumes processed, avg time-to-screen
- Top candidates widget

**Step 6 — Job Management**
- `JobListPage.tsx` — table with status badges; create button
- `CreateJobPage.tsx` — rich text JD area; `POST /jobs` triggers JD embedding

**Step 7 — Resume Upload**
- `react-dropzone` multi-file zone (PDF/DOCX)
- `POST /resumes/bulk` (multipart)
- Opens WebSocket on upload → real-time processing cards per resume with animated stage indicators

**Step 8 — Candidate List**
- Ranked table: overall, skills, experience, education scores
- Sortable columns; score range filter slider
- "Reveal Identity" toggle per row

**Step 9 — Candidate Detail**
- Radar chart (Recharts) — skills / experience / education
- Strengths + Gaps cards from AI analysis
- Full AI explanation text
- "Generate Feedback" button

**Step 10 — Feedback View**
- Generated feedback text display
- Copy-to-clipboard button
- "Mark as Sent" toggle

**Step 11 — API Service Layer**
- Typed Axios wrappers for all endpoints
- `useProcessingStream.ts` — WebSocket hook (connect, message handler, reconnect, cleanup)

**Step 12 — Deployment Config**
- `vercel.json` — SPA rewrite rules
- `VITE_API_URL` env var in Vercel

**Step 13 — Component Tests** — Vitest + React Testing Library

---

## Deployment (Phase 5 — All members · Week 5)

| Service | Platform | Notes |
|---|---|---|
| Frontend | **Vercel** | Auto-deploy from `frontend/`; set `VITE_API_URL` |
| Backend | **Railway** or **Render** | Dockerfile; set all env vars |
| Database | **Supabase** (free tier) | Managed PostgreSQL + file storage |
| Knowledge Graph | **Neo4j AuraDB** (free tier) | 200K nodes, 400K relationships |
| Vector DB | **Qdrant Cloud** (free 1 GB) | Semantic similarity search |
| AI/LLM | **Google Gemini API** | Free tier with rate limits |

---

## Integration Verification (Phase 6 — All members · Week 6)

1. `docker-compose up` → confirm Neo4j + Qdrant healthy
2. `alembic upgrade head` → verify tables in Supabase dashboard
3. Register two accounts (recruiter + hiring_manager)
4. Create a job posting → confirm JD vector in Qdrant + `REQUIRES_SKILL` edges in Neo4j
5. Upload 3 sample PDFs → watch WebSocket processing cards
6. Confirm ranked candidate list with scores + explanations
7. Neo4j browser → `MATCH (c:Candidate)-[:HAS_SKILL]->(s:Skill)<-[:REQUIRES_SKILL]-(j:Job) RETURN c, s, j`
8. Qdrant dashboard → confirm resume vectors stored
9. Generate feedback → verify it references specific skill matches/gaps
10. Verify hybrid scoring: structural score + vector similarity in analysis detail

---

## Key Milestones

| Milestone | Target | What's Working |
|---|---|---|
| M1 | End of Week 1 | Repo scaffolded, Docker running Neo4j + Qdrant, Supabase live |
| M2 | End of Week 3 | Backend API: auth + CRUD + DB + Neo4j/Qdrant clients |
| M3 | End of Week 4 | Full pipeline: upload PDF → graph + vectors → hybrid scores + explanation |
| M4 | End of Week 5 | Frontend integrated: complete recruiter workflow live |
| M5 | End of Week 6 | Deployed + verified end-to-end on cloud |

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Gemini API rate limits | Retry with exponential backoff; cache embeddings |
| Supabase connection limits | Connection pooling (pgBouncer built in) |
| Neo4j 200K node limit | Normalize/dedup skill names; monitor count |
| Qdrant 1 GB limit | Compress payloads; monitor usage |
| Sparse graph (bad parse) | Qdrant vector score compensates; hybrid weights auto-adjust |
| Resume parsing variance | Validate JSON schema; fallback to raw-text scoring |
| WebSocket drops | Client-side reconnect + graceful fallback to polling |

---

## Environment Variables

See `.env.example` for the full list. Required:

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API access |
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anon key |
| `NEO4J_URI` | Neo4j connection URI (`bolt://localhost:7687` or AuraDB) |
| `NEO4J_USERNAME` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |
| `QDRANT_URL` | Qdrant instance URL |
| `QDRANT_API_KEY` | Qdrant Cloud API key |
| `SECRET_KEY` | JWT signing secret |
| `CORS_ORIGINS` | Allowed frontend origins |

# RAX — Next Steps (as of April 6, 2026)

## Current Status

| Persona | Scope | Status |
|---------|-------|--------|
| **Person 1** (Backend Core) | DB, Models, Schemas, Auth, CRUD, Tests | **All 8 phases COMPLETE** |
| **Person 2** (AI Pipeline) | Agents: parser, graph, embedding, matching, scoring, feedback, websocket | Phases 1–3 done · **Phases 4–8 remaining** |
| **Person 3** (Frontend) | React UI: auth, dashboard, jobs, upload, candidates, feedback | Landing page scaffold done · **Phases 1–10 remaining** |

---

## Person 2 — AI Pipeline (Phases 4–8)

### Phase 4: EmbeddingAgent — Qdrant Implementation
- Embed resume/JD text via Gemini `text-embedding-004` → upsert into Qdrant
- Add `qdrant_client` to orchestrator, implement `run(ctx)` and `embed_job()`
- **Prereq:** `docker-compose up -d rax_qdrant` + valid `GOOGLE_API_KEY` in `.env`
- **Files:** `embedding_agent.py`, `orchestrator.py`
- **Verify:** Qdrant dashboard shows `resumes` + `job_descriptions` collections with points

### Phase 5: HybridMatchingAgent — Graph + Vector Fusion
- Structural score (Neo4j skill match), semantic score (Qdrant cosine), experience + education scores
- Weighted fusion: `0.50 × structural + 0.30 × semantic + 0.15 × experience + 0.05 × education`
- **Prereq:** Phase 3 + 4 test data in Neo4j and Qdrant
- **Files:** `hybrid_matching_agent.py`, `orchestrator.py`
- **Verify:** All sub-scores non-zero and within 0.0–1.0

### Phase 6: FeedbackAgent Finish + Full Pipeline Smoke Test
- Add `_persist_feedback()` stub, optionally add feedback stage to orchestrator
- Run `PipelineOrchestrator.run()` end-to-end with sample resume text
- **Files:** `feedback_agent.py`, `orchestrator.py`
- **Verify:** `ctx.analysis["overall_score"]` is 0–100, `ctx.error is None`

### Phase 7: WebSocket Real-Time Broadcasting
- Create `backend/app/api/routes/ws.py` with `ConnectionManager` + WS route
- `make_ws_callback(manager, job_id)` factory for status broadcasting
- Register WS router in `main.py`
- **Files:** `ws.py` (new), `main.py` (modify)
- **Verify:** `websocat ws://localhost:8000/ws/pipeline/test-job-1` receives stage events

### Phase 8: Integration with Person 1's Routes (UNBLOCKED)
- Wire `PipelineOrchestrator.run()` as `BackgroundTask` in `POST /resumes/upload`
- Wire `EmbeddingAgent.embed_job()` + `GraphIngestionAgent.ingest_job()` in `POST /jobs`
- Wire `FeedbackAgent.run()` in `POST /feedback`
- Implement DB persistence in `ScoringAgent` → write to `analyses` table
- Implement DB persistence in `FeedbackAgent` → write to `feedback` table
- Add WebSocket auth (validate JWT from query param)
- **Note:** Person 1's interfaces are all available: `get_db()`, `get_neo4j_driver()`, `get_qdrant_client()`, models, routes

---

## Person 3 — Frontend (Phases 1–10)

### Phase 1: Project Setup + Deps + Tailwind + shadcn/ui
- Install: `react-router-dom`, `axios`, `zustand`, `react-hook-form`, `zod`, `react-dropzone`, `recharts`
- Configure Tailwind + shadcn/ui, set up folder structure (`services/`, `store/`, `hooks/`, `types/`)
- Configure `vite.config.ts` to proxy `/api` → `http://localhost:8000`

### Phase 2: Auth (Store + Service + Pages)
- Create `authStore.ts` (zustand), `api.ts` (axios + JWT interceptor), `authService.ts`
- Build `LoginPage.tsx`, `RegisterPage.tsx`, `ProtectedRoute.tsx`
- **Can mock initially** — wire real API when ready

### Phase 3: App Shell + Routing
- Build `AppShell.tsx` with sidebar navigation
- Route structure: `/login`, `/register`, `/dashboard`, `/jobs`, `/jobs/new`, `/jobs/:id`, `/upload/:jobId`, `/candidates/:jobId`, `/candidates/:jobId/:resumeId`, `/feedback/:id`

### Phase 4: Dashboard
- `DashboardPage.tsx` with summary cards (active jobs, total resumes, avg time-to-screen)
- Top 5 candidates widget — can stub data initially

### Phase 5: Job Management
- `JobListPage.tsx` — table with status badges
- `CreateJobPage.tsx` — title + description + requirements form
- `JobDetailPage.tsx` — read-only view + action buttons

### Phase 6: Resume Upload + WebSocket Live Processing
- `UploadPage.tsx` with `react-dropzone` drag-and-drop
- `useProcessingStream.ts` WebSocket hook → `ProcessingCard.tsx` per-resume stage progress
- Upload flow: drop files → `POST /api/resumes/upload` → open WS → animate stages

### Phase 7: Candidate Ranking
- `CandidateListPage.tsx` — ranked table sorted by `overall_score`, filterable
- Score badges, pipeline status indicators

### Phase 8: Candidate Detail + Analysis
- `CandidateDetailPage.tsx` — full scoring breakdown with radar chart (recharts)
- Strengths, gaps, explanation display
- `GET /api/resumes/{resume_id}/analysis`

### Phase 9: Feedback
- `FeedbackPage.tsx` — generate + view feedback
- `POST /api/feedback/{candidate_id}/{job_id}` trigger, `GET /api/feedback/{id}` display

### Phase 10: Polish
- Loading skeletons, error boundaries, toast notifications, responsive design, dark mode

---

## Cross-Cutting Prerequisites

| Action | When | Command |
|--------|------|---------|
| Start Docker services (Neo4j + Qdrant) | Before Person 2 Phase 4+ | `docker-compose up -d` |
| Configure `.env` with real `DATABASE_URL` | Before DB migration | Copy from `.env.example` |
| Run Alembic migration | Before any live DB usage | `cd backend && alembic upgrade head` |
| Set `GOOGLE_API_KEY` in `.env` | Before Person 2 Phase 4+ | Gemini API key |
| Install frontend deps | Before Person 3 Phase 1 | `cd frontend && npm install` |
| Install backend deps | Already done | `cd backend && pip install -r requirements.txt` |

---

## Parallelization Opportunities

- **Person 2 Phases 4–7** and **Person 3 Phases 1–5** can run in parallel (no dependencies between them)
- Person 3 Phase 6 (WebSocket UI) depends on Person 2 Phase 7 (WebSocket endpoint)
- Person 2 Phase 8 (DB integration) can start immediately — Person 1's work is complete
- Person 3 can mock all API calls until backend is fully running

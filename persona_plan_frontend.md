# RAX — Frontend Persona Plan (Person 3)

> **Owner:** Person 3 — Frontend (React, TypeScript, Real-Time UI, Dashboards)
> **Scope:** `frontend/` (entire directory)
> **Do NOT touch:** `backend/` (Person 1 + Person 2 own this)

---

## What Already Exists

Person 3's Vite + React scaffold already exists:

```
frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── components/
│   ├── pages/
│   ├── lib/
│   └── assets/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

---

## Interface Contract

### What Person 1 (Backend Core) provides to you:
All endpoints are under `/api/` prefix. Base URL configured via `VITE_API_URL` env var.

| Method | Endpoint | Request | Response | Auth |
|---|---|---|---|---|
| `POST` | `/api/auth/register` | `{ email, password, full_name, role }` | `{ id, email, role }` | None |
| `POST` | `/api/auth/login` | `{ email, password }` | `{ access_token, token_type }` | None |
| `GET` | `/api/jobs` | — | `[{ id, title, status, created_at }]` | JWT |
| `POST` | `/api/jobs` | `{ title, description, requirements_raw }` | `{ id, title, status }` | JWT (recruiter) |
| `GET` | `/api/jobs/{id}` | — | `{ id, title, description, ... }` | JWT |
| `POST` | `/api/resumes/upload` | `multipart: files[], job_id` | `[{ resume_id, status }]` | JWT (recruiter) |
| `GET` | `/api/resumes/{id}/status` | — | `{ resume_id, pipeline_status, stage }` | JWT |
| `GET` | `/api/jobs/{job_id}/candidates` | `?sort_by=overall_score&order=desc` | `[{ candidate, scores, explanation }]` | JWT |
| `GET` | `/api/resumes/{resume_id}/analysis` | — | `{ overall, skills, experience, education, strengths[], gaps[], explanation }` | JWT |
| `POST` | `/api/feedback/{candidate_id}/{job_id}` | — | `{ id, content, created_at }` | JWT (recruiter) |
| `GET` | `/api/feedback/{id}` | — | `{ id, content, sent_at }` | JWT |

### What Person 2 (AI Pipeline) provides to you:
| Protocol | Endpoint | Message Format |
|---|---|---|
| WebSocket | `WS /ws/pipeline/{job_id}` | `{ resume_id, stage, status, timestamp, score? }` |

**WebSocket stages (in order):** `parsing` → `filtering` → `graph_ingestion` → `embedding` → `hybrid_matching` → `scoring` → `completed` (or `failed`)

### JWT Token Usage:
- Stored in localStorage or zustand store
- Sent as: `Authorization: Bearer <token>`
- Decoded payload: `{ sub: user_id, role: "recruiter"|"hiring_manager", exp: timestamp }`

---

## Phased Plan

### Phase 1: Project Setup + Deps + Tailwind + shadcn/ui
> **Goal:** Install all deps, configure Tailwind + shadcn/ui, set up project structure.
> **Depends on:** Nothing — fully independent
> **Commands:**
> ```bash
> cd frontend
> npm install react-router-dom axios zustand react-hook-form @hookform/resolvers zod react-dropzone recharts
> npx tailwindcss init -p
> npx shadcn-ui@latest init
> ```
>
> **Create folder structure:**
> ```
> frontend/src/
> ├── components/
> │   ├── ui/               # shadcn/ui components (auto-generated)
> │   └── layout/
> │       ├── AppShell.tsx   # sidebar + main content area
> │       └── ProtectedRoute.tsx
> ├── pages/
> ├── services/
> │   ├── api.ts            # Axios instance with base URL + JWT interceptor
> │   └── authService.ts
> ├── store/
> │   └── authStore.ts      # Zustand store
> ├── hooks/
> │   └── useProcessingStream.ts  # WebSocket hook (stub)
> ├── types/
> │   └── index.ts          # TypeScript interfaces matching API responses
> └── lib/
>     └── utils.ts          # shadcn/ui utility (auto-generated)
> ```
>
> **Configure:**
> - `vite.config.ts` — proxy `/api` to `http://localhost:8000` for dev
> - `.env` — `VITE_API_URL=http://localhost:8000`
>
> **Test:** `npm run dev` → blank app loads with Tailwind styles working

### Phase 2: Auth (Store + Service + Pages)
> **Goal:** Login/Register pages, JWT storage, protected routing.
> **Depends on:** Phase 1
> **Creates:**
> ```
> src/store/authStore.ts       # { token, user, login(), logout(), isAuthenticated }
> src/services/api.ts          # Axios instance, JWT header interceptor, 401 auto-logout
> src/services/authService.ts  # login(email, pw), register(email, pw, name, role)
> src/pages/LoginPage.tsx      # email + password form (react-hook-form + zod)
> src/pages/RegisterPage.tsx   # email + password + role selector
> src/components/layout/ProtectedRoute.tsx  # redirect to /login if no token
> ```
>
> **Can test without backend:** Mock the auth service to return a fake token. Wire real API when Person 1 delivers Phase 5.
>
> **Test:** Register → login → redirected to dashboard → logout → redirected to login

### Phase 3: App Shell + Routing
> **Goal:** Sidebar navigation, route structure, layout wrapper.
> **Depends on:** Phase 2
> **Creates:**
> ```
> src/components/layout/AppShell.tsx   # sidebar: Dashboard, Jobs, Upload, Candidates
> src/App.tsx                          # React Router routes
> ```
>
> **Routes:**
> ```
> /login          → LoginPage
> /register       → RegisterPage
> /dashboard      → DashboardPage (protected)
> /jobs           → JobListPage (protected)
> /jobs/new       → CreateJobPage (protected)
> /jobs/:id       → JobDetailPage (protected)
> /upload/:jobId  → UploadPage (protected)
> /candidates/:jobId → CandidateListPage (protected)
> /candidates/:jobId/:resumeId → CandidateDetailPage (protected)
> /feedback/:id   → FeedbackPage (protected)
> ```
>
> **Test:** Navigate between pages with sidebar; protected routes redirect

### Phase 4: Dashboard
> **Goal:** Summary cards + top candidates widget.
> **Depends on:** Phase 3
> **Creates:**
> ```
> src/pages/DashboardPage.tsx
> src/services/dashboardService.ts    # GET /api/jobs (count), aggregate stats
> ```
>
> **Cards:** Active jobs count, Total resumes processed, Avg time-to-screen
> **Widget:** Top 5 candidates across all jobs (by overall_score)
>
> **Can stub data:** Use hardcoded stats until Person 1's APIs are ready

### Phase 5: Job Management
> **Goal:** Job listing + create job page.
> **Depends on:** Phase 3
> **Creates:**
> ```
> src/pages/JobListPage.tsx     # table with status badges (Active/Closed/Draft), create button
> src/pages/CreateJobPage.tsx   # title + description textarea + requirements textarea
> src/pages/JobDetailPage.tsx   # read-only job view + "Upload Resumes" + "View Candidates" buttons
> src/services/jobService.ts    # CRUD: getJobs(), createJob(), getJob(id)
> ```
>
> **Test:** Create job → appears in list → click to view detail

### Phase 6: Resume Upload + WebSocket Live Processing
> **Goal:** Drag-and-drop upload + real-time pipeline status cards.
> **Depends on:** Phase 5 (needs a job to upload to)
> **Creates:**
> ```
> src/pages/UploadPage.tsx                  # react-dropzone + processing cards
> src/hooks/useProcessingStream.ts          # WebSocket hook (connect, onMessage, reconnect)
> src/components/ProcessingCard.tsx          # per-resume stage progress UI
> src/services/resumeService.ts             # uploadResumes(files, jobId)
> ```
>
> **Upload flow:**
> 1. User drops PDF/DOCX files → `POST /api/resumes/upload` (multipart)
> 2. On success → open WebSocket `WS /ws/pipeline/{job_id}`
> 3. Each message updates the `ProcessingCard` for that `resume_id`
> 4. Stages animate: parsing ● → filtering ● → graph ● → embed ● → match ● → score ● → ✅
>
> **WebSocket hook spec:**
> ```typescript
> useProcessingStream(jobId: string) → {
>   statuses: Map<string, { stage: string, status: string, score?: number }>,
>   isConnected: boolean,
>   error: string | null
> }
> ```
>
> **Can test without backend WebSocket:** Mock `useProcessingStream` to emit timed stage events

### Phase 7: Candidate List + Candidate Detail
> **Goal:** Ranked candidate table + detailed analysis page with radar chart.
> **Depends on:** Phase 6
> **Creates:**
> ```
> src/pages/CandidateListPage.tsx    # ranked table, sortable, filterable, identity toggle
> src/pages/CandidateDetailPage.tsx  # radar chart + strengths/gaps + explanation + feedback button
> src/services/candidateService.ts   # getCandidates(jobId), getAnalysis(resumeId)
> src/components/RadarChart.tsx      # Recharts radar: skills, experience, education
> src/components/ScoreCard.tsx       # strength/gap card component
> ```
>
> **Candidate list table columns:**
> | Column | Sortable | Notes |
> |---|---|---|
> | Rank | — | Auto-numbered |
> | Name | — | Shows `[CANDIDATE_ID]` until "Reveal" toggled |
> | Overall Score | ✅ | 0–100 |
> | Skills Score | ✅ | 0–100 |
> | Experience Score | ✅ | 0–100 |
> | Education Score | ✅ | 0–100 |
> | Status | — | Pipeline status badge |
> | Actions | — | View Detail, Reveal Identity |
>
> **Score range filter:** Slider to filter candidates by minimum overall score
>
> **Candidate detail page:**
> - Radar chart (skills / experience / education)
> - Strengths cards (green) + Gaps cards (red)
> - Full AI explanation text block
> - "Generate Feedback" button → `POST /api/feedback`
>
> **Test:** View candidates for a job → click detail → see radar + explanation

### Phase 8: Feedback View
> **Goal:** Display AI-generated feedback with copy + send tracking.
> **Depends on:** Phase 7
> **Creates:**
> ```
> src/pages/FeedbackPage.tsx         # feedback text display + copy + mark sent
> src/services/feedbackService.ts    # generateFeedback(), getFeedback()
> ```
>
> **Features:**
> - Display generated feedback text (150–200 words)
> - "Copy to Clipboard" button
> - "Mark as Sent" toggle → updates `sent_at` via API
>
> **Test:** Generate feedback from candidate detail → view → copy → mark sent

### Phase 9: TypeScript Types + API Service Polish
> **Goal:** Ensure all API response types are properly typed, error handling is consistent.
> **Depends on:** Phases 4–8
> **Creates/updates:**
> ```
> src/types/index.ts    # User, Job, Candidate, Resume, Analysis, Feedback interfaces
> src/services/api.ts   # global error interceptor, loading states, retry logic
> ```
>
> **Test:** No `any` types in API calls; all errors show user-friendly toasts

### Phase 10: Deployment Config
> **Goal:** Vercel deployment, SPA routing, env vars.
> **Depends on:** Phase 9
> **Creates:**
> ```
> frontend/vercel.json   # { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
> ```
>
> **Vercel env vars:**
> - `VITE_API_URL` → Railway/Render backend URL
>
> **Test:** Deploy to Vercel → login → full workflow works against deployed backend

### Phase 11: Component Tests
> **Goal:** Vitest + React Testing Library for key flows.
> **Depends on:** Phase 10
> **Creates:**
> ```
> frontend/src/__tests__/
> ├── auth.test.tsx           # login/register form + redirect
> ├── upload.test.tsx         # file drop + processing card render
> ├── candidateList.test.tsx  # table rendering + sort + filter
> ├── candidateDetail.test.tsx # radar chart + score cards
> └── websocket.test.tsx      # useProcessingStream hook mock
> ```
>
> **Test:** `npm run test`

---

## Development Tips

### Working Without the Backend (Phases 1–7)

You can build the entire frontend **before** Person 1 or Person 2 delivers anything:

1. **Mock API responses** — Create `src/services/mockData.ts` with sample data matching the types
2. **Mock WebSocket** — `useProcessingStream` can emit fake timed events: `setTimeout(() => setStage("parsing"), 1000)` etc.
3. **Conditional mocking** — `if (import.meta.env.VITE_MOCK_API === "true")` → return mock data instead of calling Axios
4. Switch to real API by removing the mock flag when backend is ready

### Key Packages Reference

| Package | Purpose |
|---|---|
| `react-router-dom` | Client-side routing |
| `axios` | HTTP client with interceptors |
| `zustand` | Lightweight state management |
| `react-hook-form` + `zod` | Form handling + validation |
| `react-dropzone` | Drag-and-drop file upload |
| `recharts` | Radar chart for scoring visualization |
| `tailwindcss` | Utility-first CSS |
| `shadcn/ui` | Accessible component library |

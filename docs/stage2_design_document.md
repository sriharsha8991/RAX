# RAX — Resume Analysis eXpert | Stage 2 Design Document

## Slide 1: Title, Team & Value Proposition

### Project Title
**RAX — Resume Analysis eXpert**

### Target Market
- Mid-to-large enterprises with high-volume hiring needs (100+ resumes per role)
- Staffing agencies and recruitment process outsourcing (RPO) firms
- Remote-first and distributed HR teams seeking collaborative screening tools
- Organizations under regulatory pressure (DEI mandates, EEOC compliance)

### Value Propositions
| # | Value Proposition |
|---|---|
| 1 | **Semantic understanding over keyword matching** — eliminates false rejections caused by vocabulary mismatch between resumes and job descriptions |
| 2 | **Explainable, auditable scoring** — every decision includes human-readable justification with per-dimension scores (skills, experience, education) |
| 3 | **Bias-aware screening** — automated anonymization of names, gender signals, and institution names before evaluation |
| 4 | **Hybrid knowledge graph + vector search** — Neo4j knowledge graph provides structural reasoning and explainable paths; Qdrant vector store provides semantic discovery for fuzzy matching — combined, they deliver both precision and recall |
| 5 | **Real-time collaborative pipeline** — recruiters and hiring managers see live processing stages via WebSocket, enabling faster team alignment |
| 6 | **AI-generated candidate feedback** — constructive, professional feedback for rejected candidates improves employer brand and candidate experience |
| 7 | **Distributed, scalable architecture** — async multi-agent pipeline with cloud-native graph and vector search handles bulk uploads without blocking the system |

---

## Slide 2: Competitive Landscape & Differentiation

### Existing Commercial Competitors

| Product | Strengths | Limitations |
|---|---|---|
| **Greenhouse** | Robust ATS workflow, integrations | Keyword-based filtering; limited AI explanation |
| **Lever** | CRM + ATS hybrid, collaborative | Scoring is manual or opaque; no bias anonymization |
| **HireVue** | Video interviews, AI assessment | Focused on video; resume screening is secondary |
| **Pymetrics** | Neuroscience-based assessments | Requires candidate participation; not resume-centric |
| **Ideal (by Ceridian)** | AI screening & shortlisting | Proprietary black-box scoring; no explainability |
| **Textio** | Job description optimization | Only covers JD side; does not score candidates |

### RAX Differentiators — What Makes Us a Winner

| Differentiator | Why It Matters |
|---|---|
| **Full-pipeline explainability** | Competitors provide a score; RAX provides the *why* — strengths, gaps, and reasoning for every candidate |
| **Built-in bias anonymization** | Most ATS tools bolt on DEI features as add-ons; RAX makes anonymization a first-class pipeline stage (`BiasFilterAgent`) |
| **Multi-agent transparency** | Each pipeline stage (parse → filter → embed/ingest → match → score) is independently observable in real time, not a monolithic black box |
| **Hybrid graph + vector matching** | Neo4j knowledge graph for structural skill/experience reasoning + Qdrant for semantic similarity — no competitor combines both |
| **Graph-powered explainability** | Matching results trace explicit paths: `Candidate → HAS_SKILL → Python ← REQUIRES_SKILL ← Job` — auditable and bias-verifiable |
| **Self-enriching skill taxonomy** | Qdrant embedding proximity auto-creates `IS_SIMILAR_TO` edges in Neo4j — the graph gets smarter with every resume processed |
| **Candidate feedback generation** | No major ATS provides on-demand AI-generated constructive feedback for rejected candidates |
| **Cost-effective tech stack** | Built entirely on free-tier cloud services (Supabase, Qdrant Cloud, Neo4j AuraDB, Vercel, Gemini API) — no enterprise licensing overhead |

---

## Slide 3: Key Features & Capabilities

### 3.1 User Interface (UI) Design

| Aspect | Design Decision | Justification |
|---|---|---|
| **Interaction Model** | Web-based responsive UI (desktop-first, mobile-friendly) | Recruiters primarily work on desktop; responsive ensures mobile triage |
| **Component Library** | Tailwind CSS + shadcn/ui | Accessible, consistent components with minimal bundle size |
| **Real-Time Feedback** | WebSocket-driven live processing cards | Eliminates page-refresh polling; recruiters see each pipeline stage animate in real time |
| **Data Visualization** | Radar charts (Recharts) for multi-dimension scoring | At-a-glance comparison of skills / experience / education scores |
| **Accessibility** | WCAG 2.1 AA compliance target | Keyboard navigation, screen reader support, ARIA labels on all interactive components |
| **Identity Toggle** | "Reveal Identity" per-candidate toggle | Supports blind screening workflow; recruiters can unmask only after scoring |

#### Core UI Screens

1. **Dashboard** — Summary cards (active jobs, resumes processed, avg time-to-screen), top candidates widget
2. **Job Management** — Create/edit job postings with rich text JD; status badges (Active, Closed, Draft)
3. **Resume Upload** — Drag-and-drop multi-file zone (PDF/DOCX); real-time WebSocket processing cards per resume
4. **Candidate List** — Ranked table with sortable score columns, score-range filter slider, identity reveal toggle
5. **Candidate Detail** — Radar chart, strengths/gaps cards, full AI explanation, "Generate Feedback" action
6. **Feedback View** — AI-generated feedback text with copy-to-clipboard and "Mark as Sent" toggle
7. **Auth Pages** — Login / Register with role selection (Recruiter | Hiring Manager)

### 3.2 Content Strategy

| Content Type | Description |
|---|---|
| **Job Descriptions** | Stored as structured rich text; embedded into vector space (Qdrant) and decomposed into graph nodes with `REQUIRES_SKILL` / `REQUIRES_DEGREE` relationships (Neo4j) |
| **Parsed Resumes** | Structured JSON (skills, experience, education, contact) extracted by AI — decomposed into graph entities (Neo4j) and embedded as vectors (Qdrant) |
| **AI Explanations** | Per-candidate natural language justification covering strengths, gaps, and scoring rationale |
| **Candidate Feedback** | 150–200 word constructive, professional email text generated on demand |
| **Anonymized Data** | Bias-filtered resume variant with redacted names, gender signals, and institution identifiers |

### 3.3 Feature Breakdown

| Feature | Description | Pipeline Stage |
|---|---|---|
| **Semantic Resume Parsing** | Extracts structured data from PDF/DOCX using LLM (Gemini) — not regex | `ResumeParserAgent` |
| **Bias Anonymization** | Redacts name, gender signals, university names to `[UNIVERSITY]` before scoring | `BiasFilterAgent` |
| **Knowledge Graph Ingestion** | Decomposes parsed resume into graph nodes (Skill, Company, Role, Education) and typed relationships in Neo4j | `GraphIngestionAgent` |
| **Vector Embedding** | Embeds filtered resumes and JDs into 768-dim vector space using Gemini `text-embedding-004` into Qdrant | `EmbeddingAgent` |
| **Hybrid Matching** | Fuses Neo4j graph traversal (structural skill/experience match) with Qdrant cosine similarity (semantic match) into a weighted composite score | `HybridMatchingAgent` |
| **Explainable Scoring** | Multi-dimensional scoring (overall, skills, experience, education) with natural language explanation referencing graph paths | `ScoringAgent` |
| **On-Demand Feedback** | AI-generated constructive candidate feedback referencing specific skill matches and gaps from graph | `FeedbackAgent` |
| **Skill Taxonomy** | Hierarchical skill clusters (`Python → Programming Language → Technical Skills`) with auto-discovered `IS_SIMILAR_TO` edges | Neo4j Graph |
| **Bulk Processing** | Upload multiple resumes at once; GraphIngestion + Embedding run in parallel per resume | `PipelineOrchestrator` |
| **Real-Time Status** | WebSocket pushes per-resume stage updates (parsing → filtering → ingestion → matching → scoring → completed) | WebSocket Channel |
| **Role-Based Access** | JWT auth with Recruiter and Hiring Manager roles; protected routes | Auth Middleware |

---

## Slide 4: Workflows

### 4.1 Recruiter Workflow (Primary Use Case)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RECRUITER WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. LOGIN ──► 2. CREATE JOB POSTING ──► 3. UPLOAD RESUMES (bulk)   │
│                    │                          │                      │
│                    ▼                          ▼                      │
│           JD embedded into              Pipeline runs               │
│           Qdrant & decomposed           automatically               │
│           into Neo4j graph                    │                      │
│                                               ▼                      │
│               4. MONITOR LIVE PROCESSING (WebSocket)                │
│                  [parsing → filtering → graph ingestion +            │
│                   embedding → hybrid matching → scoring              │
│                   → completed]                                       │
│                                               │                      │
│                                               ▼                      │
│               5. REVIEW RANKED CANDIDATES                           │
│                  (sorted by overall score, filterable)               │
│                                               │                      │
│                  ┌────────────────────────────┼──────────┐          │
│                  ▼                            ▼          ▼          │
│          6a. VIEW DETAIL            6b. TOGGLE      6c. GENERATE   │
│          (radar chart,               IDENTITY        FEEDBACK      │
│           strengths/gaps,            REVEAL          (AI email)     │
│           explanation)                                              │
│                                                         │          │
│                                                         ▼          │
│                                               7. SEND FEEDBACK     │
│                                                  (copy / mark sent)│
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 AI Pipeline Workflow (Backend)

```
Resume Upload (PDF/DOCX)
        │
        ▼
┌────────────────────┐
│ ResumeParserAgent    │  Extract text → LLM structured JSON
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ BiasFilterAgent      │  Anonymize name, gender, institution
└─────────┬──────────┘
          │
    ┌─────┴─────┐          (parallel execution)
    ▼              ▼
┌────────────┐  ┌────────────┐
│ GraphIngest. │  │ Embedding  │
│ Agent       │  │ Agent      │
│ → Neo4j     │  │ → Qdrant   │  Decompose into graph + Embed into vectors
└──────┬─────┘  └─────┬──────┘
       └──────┬──────┘
              ▼
┌───────────────────────┐
│ HybridMatchingAgent   │  Graph traversal (Neo4j) + cosine similarity (Qdrant)
└─────────┬─────────────┘  → fused weighted score
          ▼
┌────────────────────┐
│ ScoringAgent         │  Gemini prompt with hybrid context → multi-dim scores + explanation
└─────────┬──────────┘
          ▼
   Analysis stored in DB
   Status pushed via WebSocket
```

### 4.3 Data Flow Summary

```
User Uploads Resume
  → File stored (Supabase Storage)
  → Raw text extracted (ResumeParserAgent)
  → Structured JSON parsed (Gemini LLM)
  → PII anonymized (BiasFilterAgent)
  → [parallel] Graph entities ingested (GraphIngestionAgent → Neo4j)
  → [parallel] Vector embedded (EmbeddingAgent → Qdrant)
  → Hybrid match computed (HybridMatchingAgent ← Neo4j graph traversal + Qdrant cosine similarity)
  → Scores & explanation generated (ScoringAgent → Supabase PostgreSQL)
  → Results pushed to frontend (WebSocket)
  → Displayed in ranked candidate table
```

---

## Slide 5: System Architecture

### High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT TIER                                   │
│                                                                            │
│    ┌──────────────────────────────────────────────────────────────┐        │
│    │           React + TypeScript Frontend (Vite)                 │        │
│    │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │        │
│    │  │ Auth     │  │ Job Mgmt  │  │ Upload + │  │ Candidate │  │        │
│    │  │ Pages    │  │ Pages     │  │ Live WS  │  │ Dashboard │  │        │
│    │  └──────────┘  └───────────┘  └──────────┘  └───────────┘  │        │
│    │         Zustand State │ Axios HTTP │ WebSocket              │        │
│    └────────────────────────┼───────────┼───────────────────────┘        │
│                              │           │                                 │
│                     Deployed on Vercel                                     │
└──────────────────────────────┼───────────┼─────────────────────────────────┘
                               │ REST API  │ WS
┌──────────────────────────────┼───────────┼─────────────────────────────────┐
│                              SERVER TIER                                   │
│                                                                            │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                  FastAPI Backend                             │         │
│    │  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │         │
│    │  │ Auth     │  │ Jobs API  │  │ Resumes   │  │ WS       │ │         │
│    │  │ Routes   │  │ Routes    │  │ API       │  │ Endpoint │ │         │
│    │  └──────────┘  └───────────┘  └─────┬─────┘  └──────────┘ │         │
│    │                                      │                      │         │
│    │              ┌───────────────────────┘                      │         │
│    │              ▼                                               │         │
│    │  ┌─────────────────────────────────────────────────┐       │         │
│    │  │           Pipeline Orchestrator                   │       │         │
│    │  │  ┌────────┐ ┌───────┐ ┌─────────┐ ┌──────────┐ │       │         │
│    │  │  │ Resume │→│ Bias  │→│Embedding│→│ Matching │ │       │         │
│    │  │  │ Parser │ │Filter │ │ Agent   │ │ Agent    │ │       │         │
│    │  │  └────────┘ └───────┘ └─────────┘ └──────────┘ │       │         │
│    │  │                                          ↓       │       │         │
│    │  │  ┌──────────┐              ┌──────────┐          │       │         │
│    │  │  │ Feedback │ (on demand)  │ Scoring  │          │       │         │
│    │  │  │ Agent    │              │ Agent    │          │       │         │
│    │  │  └──────────┘              └──────────┘          │       │         │
│    │  └─────────────────────────────────────────────────┘       │         │
│    └─────────────────────────────────────────────────────────────┘         │
│                     Deployed on Railway / Render                           │
└──────────────┬────────────────────┬────────────────────┬──────────────────┘
               │                    │                    │
┌──────────────┼────────┐ ┌────────┼─────────┐ ┌────────┼──────────────────┐
│  DATA TIER   │        │ │ VECTOR TIER      │ │   AI TIER                │
│              ▼        │ │        ▼         │ │        ▼                  │
│  ┌──────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────────────┐ │
│  │ Supabase         │ │ │ │ Qdrant       │ │ │ │ Google Gemini API    │ │
│  │ (PostgreSQL)     │ │ │ │ (Vector DB)  │ │ │ │                      │ │
│  │                  │ │ │ │              │ │ │ │ • gemini-1.5-pro     │ │
│  │ • Users          │ │ │ │ • resumes    │ │ │ │   (parsing, scoring, │ │
│  │ • Jobs           │ │ │ │   collection │ │ │ │    feedback)         │ │
│  │ • Candidates     │ │ │ │ • job_descs  │ │ │ │                      │ │
│  │ • Resumes        │ │ │ │   collection │ │ │ │ • text-embedding-004 │ │
│  │ • Analyses       │ │ │ │              │ │ │ │   (vector embeddings)│ │
│  │ • Feedback       │ │ │ │ Cosine       │ │ │ │                      │ │
│  │                  │ │ │ │ Similarity   │ │ │ └──────────────────────┘ │
│  │ + Supabase       │ │ │ │ Search       │ │ │                          │
│  │   Storage        │ │ │ └──────────────┘ │ │   Deployed: Google Cloud │
│  │   (resume files) │ │ │                  │ │                          │
│  └──────────────────┘ │ │ Deployed:        │ └──────────────────────────┘
│                       │ │ Qdrant Cloud     │
│  Deployed:            │ └──────────────────┘
│  Supabase Cloud       │
└───────────────────────┘
```

### Technology Stack Summary

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React.js + TypeScript (Vite) | SPA with real-time WebSocket support |
| **UI Framework** | Tailwind CSS + shadcn/ui | Accessible, responsive component library |
| **State Management** | Zustand | Lightweight client-side state |
| **Backend** | Python FastAPI | Async REST API + WebSocket server |
| **Auth** | JWT (python-jose + passlib) | Stateless role-based authentication |
| **Database** | Supabase (PostgreSQL) | Relational data, user/job/candidate records |
| **File Storage** | Supabase Storage | Resume PDF/DOCX file storage |
| **Knowledge Graph** | Neo4j (AuraDB / Docker) | Structured entities, skill taxonomy, explainable matching |
| **Vector Database** | Qdrant | Semantic similarity search on embeddings |
| **LLM** | Google Gemini (gemini-1.5-pro) | Resume parsing, scoring, feedback generation |
| **Embeddings** | Gemini text-embedding-004 | 768-dim vector representations |
| **Real-Time** | WebSocket (FastAPI native) | Live pipeline status updates |
| **Migrations** | Alembic | Database schema versioning |
| **Deployment** | Vercel / Railway / Neo4j AuraDB / Qdrant Cloud / Supabase | Fully cloud-hosted, free-tier compatible |

### Data Model (Entity Relationships)

```
┌──────────┐       ┌──────────┐       ┌────────────┐
│  User    │       │   Job    │       │ Candidate  │
│──────────│       │──────────│       │────────────│
│ id (PK)  │──┐   │ id (PK)  │──┐   │ id (PK)    │──┐
│ email    │  │   │ title    │  │   │ name       │  │
│ password │  │   │ desc     │  │   │ email      │  │
│ role     │  └──►│ created_ │  │   └────────────┘  │
│ created_ │      │   by(FK) │  │                    │
└──────────┘      │ embed_id │  │   ┌────────────┐  │
                  └──────────┘  │   │  Resume     │  │
                       │        │   │────────────│  │
                       │        └──►│ job_id(FK) │  │
                       │            │ cand_id(FK)│◄─┘
                       │            │ raw_text   │──┐
                       │            │ parsed_json│  │
                       │            │ embed_id   │  │
                       │            │ status     │  │
                       │            └────────────┘  │
                       │                            │
                       │            ┌────────────┐  │
                       │            │ Analysis   │  │
                       │            │────────────│  │
                       │            │ resume_id  │◄─┘
                       │            │ overall_   │
                       │            │ skills_    │
                       │            │ experience_│
                       │            │ education_ │
                       │            │ explanation│
                       │            │ strengths  │
                       │            │ gaps       │
                       │            └────────────┘
                       │
                       │            ┌────────────┐
                       │            │ Feedback   │
                       │            │────────────│
                       └───────────►│ job_id(FK) │
                                    │ cand_id(FK)│
                                    │ content    │
                                    │ sent_at    │
                                    └────────────┘
```

### Distributed Computing Aspects

| Aspect | Implementation |
|---|---|
| **Async Pipeline** | Each agent runs as an async task; multiple resumes processed concurrently via FastAPI `BackgroundTask`; GraphIngestion + Embedding run in parallel |
| **Graph Traversal** | Neo4j provides native graph traversal for structural skill matching; Cypher queries return explainable paths in sub-millisecond time |
| **Vector Search Distribution** | Qdrant Cloud provides distributed vector indexing and sub-millisecond cosine similarity queries for semantic matching |
| **Hybrid Score Fusion** | HybridMatchingAgent combines graph structural score (Neo4j) + semantic similarity score (Qdrant) with configurable weights |
| **Self-Enriching Graph** | Qdrant embedding proximity auto-discovers `IS_SIMILAR_TO` skill edges, enriching Neo4j taxonomy with every resume processed |
| **Database Scalability** | Supabase PostgreSQL with connection pooling; read replicas available on scaling tier |
| **Stateless Backend** | JWT auth + no server-side sessions = horizontal scaling via multiple Railway/Render instances |
| **Event-Driven Updates** | In-memory pub/sub over WebSocket; each pipeline stage publishes completion events independently |
| **Cloud-Native Storage** | Resume files in Supabase Storage (S3-compatible); vectors in Qdrant Cloud; graph in Neo4j AuraDB — no local disk dependency |

---

## Slide 6: Conclusion & Implementation Plan

### Conclusion

RAX addresses the core failures of traditional ATS platforms — keyword brittleness, opaque decisions, and embedded bias — by replacing them with a semantic, explainable, and bias-aware multi-agent AI pipeline. The hybrid architecture combining **Neo4j knowledge graph** (structural reasoning, skill taxonomy, explainable paths) with **Qdrant vector search** (semantic discovery, fuzzy matching) delivers both precision and recall — no competitor offers both. Together with **per-candidate explainability**, **automated anonymization**, and **real-time collaborative processing**, RAX is a differentiated solution in a market dominated by black-box systems.

The architecture is designed for free-tier cloud deployment (Supabase, Neo4j AuraDB, Qdrant Cloud, Vercel), making it viable as both an academic prototype and a production-ready MVP without licensing costs.

### Implementation Plan

| Phase | Scope | Owner | Timeline |
|---|---|---|---|
| **Phase 0** | Project scaffolding, repo setup, Docker Compose (Neo4j + Qdrant), Supabase project creation, env configuration | Shared (All) | Week 1 |
| **Phase 1** | Backend core — FastAPI bootstrap, SQLAlchemy models, Supabase DB integration, Neo4j client, Qdrant client, auth (JWT), CRUD API routes, Alembic migrations | Person 1 | Weeks 2–3 |
| **Phase 2** | AI pipeline — ResumeParser, BiasFilter, GraphIngestion (Neo4j), Embedding (Qdrant), HybridMatching, Scoring, Feedback agents; PipelineOrchestrator | Person 2 | Weeks 2–4 |
| **Phase 3** | WebSocket real-time — pipeline status broadcasting, in-memory pub/sub manager | Person 2 | Week 4 |
| **Phase 4** | Frontend — Auth, Dashboard, Job Management, Resume Upload (with live WS), Candidate List/Detail, Feedback View | Person 3 | Weeks 2–5 |
| **Phase 5** | Deployment — Vercel (frontend), Railway/Render (backend), Neo4j AuraDB, Qdrant Cloud, Supabase Cloud | Shared (All) | Week 5 |
| **Phase 6** | Integration verification — end-to-end test with sample data, Neo4j graph validation, Qdrant vector validation, WebSocket validation, scoring quality review | Shared (All) | Week 6 |

### Key Milestones

1. **M1 (End of Week 1):** Repo scaffolded, Docker Compose running Neo4j + Qdrant, Supabase project created
2. **M2 (End of Week 3):** Backend API functional — auth, CRUD, DB connected to Supabase, Neo4j + Qdrant clients initialized
3. **M3 (End of Week 4):** Full AI pipeline operational — upload a resume, graph ingested in Neo4j, vector embedded in Qdrant, hybrid scores + explanation generated
4. **M4 (End of Week 5):** Frontend integrated with backend — complete recruiter workflow functional
5. **M5 (End of Week 6):** Deployed, tested end-to-end with sample data on cloud infrastructure

### Risk Mitigation

| Risk | Mitigation |
|---|---|
| Gemini API rate limits on free tier | Implement retry with exponential backoff; cache embeddings to avoid re-computation |
| Supabase free-tier connection limits | Use connection pooling (pgBouncer built into Supabase); optimize query patterns |
| Neo4j AuraDB free-tier limits (200K nodes) | Monitor node count; normalize/dedup skill names to minimize node proliferation |
| Qdrant Cloud 1 GB storage limit | Limit vector dimensions; compress payloads; monitor usage metrics |
| Graph sparsity on poorly parsed resumes | Qdrant vector similarity acts as fallback when graph data is insufficient; hybrid weights auto-compensate |
| Resume parsing accuracy variance | Validate parsed JSON schema; fallback to raw-text scoring if structured extraction fails |
| WebSocket reliability | Client-side reconnect logic with exponential backoff; graceful degradation to polling |

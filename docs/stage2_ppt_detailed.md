# RAX — Stage 2 Presentation (Detailed Version)

> 15-minute presentation | 6 slides | Speaker notes and talking points included

---

## SLIDE 1: Title, Team & Value Proposition

### Title
**RAX — Resume Analysis eXpert**
*AI-Powered Hiring with Explainable, Bias-Aware Multi-Agent Screening*

### Team Members
- Person 1 — Backend Core (FastAPI, Supabase, Auth, Neo4j/Qdrant clients)
- Person 2 — AI Pipeline (Gemini, Neo4j Graph Agents, Qdrant Embedding, WebSocket)
- Person 3 — Frontend (React, TypeScript, Real-Time UI, Dashboards)

### Target Market
- **Enterprise HR teams** handling 100+ resumes per open role — current ATS tools reject qualified candidates via keyword mismatch
- **Staffing agencies & RPO firms** processing thousands of resumes across clients — need fast, scalable, fair screening at volume
- **Remote-first & distributed teams** requiring real-time collaborative hiring — need shared visibility into screening progress
- **Compliance-driven organizations** under DEI mandates and EEOC regulations — need auditable, bias-free screening decisions

### Value Propositions (from Phase 1)
1. **Semantic understanding over keyword matching** — NLP-powered meaning extraction eliminates false rejections caused by vocabulary mismatch between resumes and JDs
2. **Explainable, auditable scoring** — every hiring decision includes human-readable justification with per-dimension scores (skills, experience, education) and named graph paths
3. **Bias-aware screening** — automated anonymization of names, gender signals, and institution names before any evaluation occurs
4. **Hybrid knowledge graph + vector search** — Neo4j provides structural reasoning ("this candidate has 4/5 required skills"); Qdrant provides semantic discovery ("this resume feels like a strong fit") — combined for maximum precision and recall
5. **Real-time collaborative pipeline** — recruiters and hiring managers watch live processing stages via WebSocket
6. **AI-generated candidate feedback** — constructive, professional rejection feedback improves employer brand
7. **Distributed, scalable architecture** — async multi-agent pipeline on free-tier cloud services handles bulk uploads without blocking

### Speaker Notes
> Open with the problem: "Recruiters spend 23 hours screening resumes for a single hire. 75% of resumes are rejected by ATS keyword filters — and studies show 88% of qualified candidates are filtered out. RAX solves this."
>
> Emphasize the hybrid architecture as the key innovation: we don't just do vector similarity like every other AI tool — we build a knowledge graph that reasons about WHY a candidate matches, not just HOW SIMILAR they are.

---

## SLIDE 2: Competitive Landscape & Key Winning Feature #1

### The Market Today

| Competitor | What They Do Well | What They Can't Do |
|---|---|---|
| **Greenhouse** | Robust workflow, 400+ integrations | Keyword-only filtering; no AI explanation |
| **Lever** | CRM + ATS hybrid, team collaboration | Scoring is manual or opaque; no anonymization |
| **HireVue** | AI-powered video interview assessment | Resume screening is secondary; video-only AI |
| **Pymetrics** | Neuroscience-based game assessments | Requires candidate participation; not resume-centric |
| **Ideal (Ceridian)** | AI screening and shortlisting | Black-box proprietary scoring; zero explainability |
| **Textio** | JD language optimization | Only covers the job description side; doesn't score candidates |

**The gap every competitor shares:** Opaque scoring + no structural reasoning + bias anonymization is an afterthought.

### Winning Feature #1 — Hybrid Knowledge Graph + Vector Search

**Why this is our killer differentiator:**

No existing ATS or AI hiring tool combines both approaches:

| Capability | Vector-Only Tools (competitors) | **RAX (Hybrid)** |
|---|---|---|
| "Find similar resumes" | ✅ Cosine similarity | ✅ Qdrant embeddings |
| "Explain WHY it matches" | ❌ Just a score number | ✅ Neo4j graph paths: `Candidate →HAS_SKILL→ Python ←REQUIRES_SKILL← Job` |
| Adjacent skill discovery | Partial (embedding proximity) | ✅ Both: embeddings + `IS_SIMILAR_TO` edges |
| Multi-hop reasoning | ❌ Impossible | ✅ "Worked at fintech company using same stack" |
| Skill taxonomy | ❌ Flat embeddings | ✅ `Python → Programming Language → Technical Skills` |
| Bias audit trail | ❌ Can't verify | ✅ Query graph to prove no protected attributes influenced score |
| Self-improving over time | ❌ Static model | ✅ Qdrant discovers new skill similarities → auto-creates Neo4j edges |

**How the fusion works:**
```
hybrid_score = 0.30 × semantic_similarity (Qdrant)
             + 0.50 × structural_match   (Neo4j)
             + 0.15 × experience_depth    (Neo4j)
             + 0.05 × education_fit       (Neo4j)
```
Weights are configurable per job. If the graph is sparse (poorly parsed resume), the vector score naturally compensates.

### Speaker Notes
> Walk through the competitor table quickly — the audience already knows these tools. Spend most of the time on the hybrid architecture.
>
> Key talking point: "Vector search tells you WHAT matches. Knowledge graphs tell you WHY. RAX is the first to combine both in a single hiring pipeline."
>
> Show the score fusion formula — emphasize that the weights are tunable and that the system self-compensates when one signal is weak.

---

## SLIDE 3: Key Winning Features #2 and #3

### Winning Feature #2 — Full-Pipeline Explainability

**The Problem:** Every AI hiring tool today is a black box. A recruiter sees "Score: 85" with no explanation. Candidates get generic rejection emails. Compliance teams can't audit decisions.

**RAX's Solution — Explainability at Every Layer:**

| Layer | What RAX Explains | Example Output |
|---|---|---|
| **Skill Matching** | Named graph paths showing exactly which skills matched/missed | "Direct match on 4/5 must-have skills: Python ✅, SQL ✅, AWS ✅, Docker ✅, Kubernetes ❌" |
| **Similar Skills** | Adjacent skills discovered via graph + embeddings | "Your React experience provided 87% partial credit toward the Frontend requirement" |
| **Experience Depth** | Years comparison per skill from graph properties | "3+ years surplus in Python (has 8, needs 5); 2 years gap in Kubernetes (has 0, needs 2)" |
| **Education Fit** | Degree level comparison from graph relationships | "Master's degree exceeds the required Bachelor's level" |
| **Overall Narrative** | Gemini-generated natural language explanation | "Strong technical match with deep Python and cloud experience. Primary gap is container orchestration (Kubernetes). Recommend for interview with focus on infrastructure skills." |
| **Bias Audit** | Queryable graph proving no protected attributes influenced score | Cypher: `MATCH path WHERE NOT (path)-[:USES]->(:ProtectedAttribute) RETURN path` |

**Deliverable to recruiter:** Radar chart (skills / experience / education) + strengths/gaps cards + full AI narrative + "Reveal Identity" toggle for blind screening.

### Winning Feature #3 — Bias-Aware Screening by Design

**The Problem:** Name, gender, university prestige, and nationality unconsciously influence screening decisions. Most tools address this as an optional add-on.

**RAX's Solution — Anonymization is a First-Class Pipeline Stage:**

```
Original Resume → ResumeParserAgent → Structured JSON
                                           ↓
                                    BiasFilterAgent
                                           ↓
                               Anonymized Resume:
                               • Name → [CANDIDATE_ID]
                               • "Harvard University" → [UNIVERSITY]
                               • Gender signals → removed
                               • Nationality signals → removed
                               • Age indicators → removed
```

- Anonymization runs BEFORE any scoring or matching occurs
- Recruiters see anonymized candidates by default; "Reveal Identity" is a conscious choice AFTER reviewing scores
- Graph queries can audit: "Did any path from Candidate to Score pass through institution name?" → verifiable compliance
- Supports EEOC, DEI, and EU AI Act transparency requirements

### Speaker Notes
> For explainability: show a mock candidate detail page with the radar chart and strengths/gaps. The audience should see concrete output, not just architecture.
>
> For bias: emphasize that anonymization is NOT optional — it's built into the core pipeline. Every other tool treats DEI as a checkbox; RAX treats it as architecture.
>
> Key stat: "Studies show identical resumes with 'white-sounding' names receive 50% more callbacks. RAX eliminates this by design."

---

## SLIDE 4: Key Winning Feature #4 + Workflows

### Winning Feature #4 — Real-Time Multi-Agent Pipeline with Live Visibility

**The Problem:** Traditional ATS tools process resumes in a batch with no visibility. Recruiters upload resumes and wait hours for results — no feedback on progress, no ability to monitor quality.

**RAX's Solution — Live WebSocket-Driven Processing:**

Each resume flows through 6 observable stages with real-time status cards in the browser:

```
┌─────────────────────────────────────────────────────────┐
│  Resume: john_doe_resume.pdf                            │
│                                                         │
│  ● Parsing ............ ✅ Complete (2.1s)              │
│  ● Bias Filtering ..... ✅ Complete (1.3s)              │
│  ● Graph Ingestion .... ✅ Complete (1.8s)  ┐           │
│  ● Vector Embedding ... ✅ Complete (0.9s)  ┘ parallel  │
│  ● Hybrid Matching .... ✅ Complete (0.6s)              │
│  ● Scoring ............ ✅ Complete (3.2s)              │
│                                                         │
│  Overall Score: 87/100   Skills: 91  Exp: 84  Edu: 78  │
└─────────────────────────────────────────────────────────┘
```

- Recruiters watch resumes move through the pipeline stage-by-stage in real time
- Multiple resumes process concurrently — each with its own animated status card
- If a stage fails (e.g., unparseable PDF), the recruiter sees it immediately — no silent failures
- GraphIngestion and Embedding run in parallel, reducing total pipeline time by ~30%

### End-to-End Recruiter Workflow

```
1. LOGIN → 2. CREATE JOB (JD embedded in Qdrant + decomposed into Neo4j graph)
                                          ↓
3. UPLOAD RESUMES (bulk drag-and-drop, PDF/DOCX)
                                          ↓
4. WATCH LIVE PROCESSING (WebSocket stage cards per resume)
                                          ↓
5. REVIEW RANKED CANDIDATES (sorted by hybrid score, filterable by score range)
          ↓                    ↓                    ↓
    6a. VIEW DETAIL      6b. REVEAL IDENTITY  6c. GENERATE FEEDBACK
    (radar chart,         (unblind after        (AI-written
     strengths/gaps,       reviewing scores)     rejection email)
     AI explanation)                                    ↓
                                              7. SEND FEEDBACK
                                                 (copy / mark sent)
```

### Speaker Notes
> Demo story: "Imagine you're a recruiter. You drag 50 resumes into RAX. Immediately, you see 50 live cards animating through each pipeline stage. In under 2 minutes, you have all 50 candidates ranked with explainable scores, ready for review."
>
> Emphasize parallel execution of GraphIngestion + Embedding — this is a distributed computing aspect.
>
> The WebSocket is not just a nice UI feature — it's key for team collaboration. Multiple team members can watch the same pipeline in real time.

---

## SLIDE 5: System Architecture

### Four-Tier Cloud-Native Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT TIER                           │
│  React + TypeScript (Vite) + Tailwind + shadcn/ui       │
│  Zustand state | Axios REST | WebSocket live updates    │
│  Deployed on: Vercel                                    │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API + WebSocket
┌─────────────────────────┼───────────────────────────────┐
│                    SERVER TIER                           │
│  Python FastAPI (async)                                 │
│  ┌─────────────────────────────────────────────┐        │
│  │ Pipeline Orchestrator                       │        │
│  │ ResumeParser → BiasFilter → [GraphIngestion │        │
│  │                              || Embedding]  │        │
│  │                             → HybridMatch   │        │
│  │                             → Scoring       │        │
│  │ FeedbackAgent (on demand)                   │        │
│  └─────────────────────────────────────────────┘        │
│  JWT Auth | Alembic Migrations | Background Tasks       │
│  Deployed on: Railway / Render                          │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
┌────────┼──────┐ ┌─────┼──────┐ ┌────┼───────────┐ ┌────────────────┐
│ DATA TIER     │ │ GRAPH TIER │ │ VECTOR TIER    │ │ AI TIER        │
│               │ │            │ │                │ │                │
│ Supabase      │ │ Neo4j      │ │ Qdrant         │ │ Google Gemini  │
│ (PostgreSQL)  │ │ (Knowledge │ │ (Vector DB)    │ │                │
│               │ │  Graph)    │ │                │ │ gemini-1.5-pro │
│ • Users       │ │            │ │ • resumes      │ │ (parse, score, │
│ • Jobs        │ │ • Candidate│ │   collection   │ │  feedback)     │
│ • Resumes     │ │ • Skill    │ │ • job_descs    │ │                │
│ • Analyses    │ │ • Company  │ │   collection   │ │ text-embed-004 │
│ • Feedback    │ │ • Role     │ │                │ │ (768-dim       │
│               │ │ • Education│ │ Cosine search  │ │  vectors)      │
│ + Supabase    │ │ • SkillCltr│ │                │ │                │
│   Storage     │ │            │ │ Deployed:      │ │ Deployed:      │
│   (files)     │ │ HAS_SKILL  │ │ Qdrant Cloud   │ │ Google Cloud   │
│               │ │ WORKED_AT  │ └────────────────┘ └────────────────┘
│ Deployed:     │ │ REQUIRES   │
│ Supabase      │ │ IS_SIMILAR │
│ Cloud         │ │ BELONGS_TO │
└───────────────┘ │            │
                  │ Deployed:  │
                  │ Neo4j      │
                  │ AuraDB     │
                  └────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + TypeScript (Vite) | SPA with real-time WebSocket |
| UI | Tailwind CSS + shadcn/ui | Accessible, responsive components |
| Backend | Python FastAPI | Async REST + WebSocket server |
| Auth | JWT (python-jose + passlib) | Stateless role-based access |
| Database | Supabase (PostgreSQL) | Relational data (users, jobs, scores) |
| Knowledge Graph | Neo4j | Skill taxonomy, structural matching, explainable paths |
| Vector Store | Qdrant | Semantic similarity, fuzzy matching |
| LLM | Google Gemini (gemini-1.5-pro) | Parsing, scoring, feedback generation |
| Embeddings | Gemini text-embedding-004 | 768-dim vector representations |
| Real-Time | WebSocket (FastAPI native) | Live pipeline progress |
| Deployment | Vercel / Railway / Neo4j AuraDB / Qdrant Cloud / Supabase | All free-tier cloud |

### Neo4j Knowledge Graph Schema (Key Nodes & Relationships)

```
(Candidate)-[:HAS_SKILL {years, proficiency}]->(Skill)
(Job)-[:REQUIRES_SKILL {priority, min_years}]->(Skill)
(Skill)-[:IS_SIMILAR_TO {score}]->(Skill)          ← auto-discovered from Qdrant
(Skill)-[:BELONGS_TO]->(SkillCluster)
(Candidate)-[:WORKED_AT {duration}]->(Company)
(Candidate)-[:HELD_ROLE]->(Role)
(Candidate)-[:HAS_DEGREE]->(Education)
(Candidate)-[:STUDIED_AT]->(Institution)
(Job)-[:REQUIRES_DEGREE {min_level}]->(Education)
```

### Distributed Computing Aspects
- **Parallel agent execution:** GraphIngestion + Embedding run concurrently per resume
- **Async pipeline:** multiple resumes processed via FastAPI BackgroundTask
- **Stateless backend:** JWT auth enables horizontal scaling across multiple instances
- **Cloud-native storage:** No local disk — Supabase Storage (files), Qdrant Cloud (vectors), Neo4j AuraDB (graph)
- **Event-driven updates:** WebSocket pub/sub per pipeline stage
- **Self-enriching graph:** Qdrant embedding proximity auto-creates `IS_SIMILAR_TO` edges in Neo4j

### Speaker Notes
> Walk through the four tiers top-to-bottom. Emphasize:
> 1. The backend is a PIPELINE, not a monolith — each agent is independent and testable
> 2. Neo4j and Qdrant serve different purposes — graph for structure, vectors for semantics
> 3. The entire stack runs on free-tier cloud services — $0 infrastructure cost for MVP
> 4. The self-enriching graph is a unique technical innovation — the system learns as it processes
>
> Optional: if time permits, show the Neo4j graph schema and explain one Cypher query for skill matching.

---

## SLIDE 6: Conclusion & Implementation Plan

### Why RAX Wins

| What Competitors Do | What RAX Does Differently |
|---|---|
| Keyword matching | Semantic understanding (Gemini LLM) |
| Black-box scoring | Full explainability (graph paths + AI narrative) |
| Bias as afterthought | Anonymization as core pipeline stage |
| Vector-only similarity | Hybrid graph + vector matching |
| Batch processing | Real-time WebSocket with live stage visibility |
| No candidate feedback | AI-generated constructive rejection feedback |
| Expensive enterprise tools | 100% free-tier cloud deployment |

### Implementation Plan

| Phase | What | Who | When |
|---|---|---|---|
| **0** | Repo scaffold, Docker (Neo4j + Qdrant), Supabase setup | All | Week 1 |
| **1** | Backend: FastAPI, DB models, auth, CRUD APIs, Neo4j + Qdrant clients | Person 1 | Weeks 2–3 |
| **2** | AI Pipeline: all 6 agents + orchestrator | Person 2 | Weeks 2–4 |
| **3** | WebSocket real-time broadcasting | Person 2 | Week 4 |
| **4** | Frontend: all screens + WebSocket integration | Person 3 | Weeks 2–5 |
| **5** | Cloud deployment (Vercel, Railway, AuraDB, Qdrant Cloud) | All | Week 5 |
| **6** | End-to-end integration testing + demo prep | All | Week 6 |

### Key Milestones
1. **Week 1:** Repo ready, Docker running Neo4j + Qdrant, Supabase project live
2. **Week 3:** Backend API functional with auth + CRUD + database connected
3. **Week 4:** Full pipeline works — upload PDF → get hybrid scores + explanation
4. **Week 5:** Complete recruiter workflow live in frontend
5. **Week 6:** Deployed and verified end-to-end on cloud infrastructure

### Risk Mitigation Summary

| Risk | How We Handle It |
|---|---|
| Gemini API rate limits | Retry + exponential backoff; cache embeddings |
| Neo4j 200K node limit (free tier) | Normalize/dedup skill names; monitor node count |
| Qdrant 1 GB limit | Compress payloads; monitor usage |
| Poorly parsed resumes | Qdrant vector score compensates for sparse graph data |
| WebSocket drops | Client-side reconnect; graceful fallback to polling |

### Closing Statement

> RAX is not just another AI hiring tool. It's the first platform that combines **structural reasoning** (knowledge graph) with **semantic discovery** (vector search) to deliver both precision and explainability. Every decision is auditable, every screening is bias-filtered by design, and every candidate gets a fair evaluation.
>
> The architecture runs entirely on free-tier cloud services, the pipeline is fully distributed and observable in real time, and the system gets smarter with every resume it processes.
>
> We're ready to build. Thank you.

### Speaker Notes
> End strong with the closing statement. Emphasize three things:
> 1. No other tool combines graph + vector matching
> 2. The system actively gets smarter over time (self-enriching graph)
> 3. Zero infrastructure cost — entirely built on free-tier services
>
> If questions come about feasibility: point to the phased plan, the modular agent design, and the fact that all technologies are battle-tested (Neo4j, Qdrant, FastAPI, Gemini).

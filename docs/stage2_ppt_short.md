# RAX — Stage 2 Presentation (PPT Slide Version)

> Copy-paste ready for slides. Short, visual, to the point.

---

## SLIDE 1 — Title & Value Proposition

**RAX — Resume Analysis eXpert**
*AI-Powered Hiring | Explainable | Bias-Free | Real-Time*

**Team:** Person 1 (Backend) · Person 2 (AI Pipeline) · Person 3 (Frontend)

**Target Market:**
- Enterprise HR teams (100+ resumes/role)
- Staffing agencies & RPO firms
- Compliance-driven orgs (DEI, EEOC)

**Value Propositions:**
1. Semantic understanding replaces keyword matching
2. Every score comes with a full explanation (strengths, gaps, reasoning)
3. Names, gender, institutions anonymized before evaluation
4. Hybrid Knowledge Graph + Vector Search — structural reasoning + semantic discovery
5. Real-time WebSocket pipeline — watch resumes process live
6. AI-generated feedback for rejected candidates
7. 100% free-tier cloud deployment

---

## SLIDE 2 — Competitive Analysis & Winning Feature #1

**Competitor Gaps:**

| Tool | Limitation |
|---|---|
| Greenhouse | Keyword-only; no AI explanation |
| Lever | Manual/opaque scoring; no anonymization |
| HireVue | Video-only; no resume intelligence |
| Ideal (Ceridian) | Black-box AI; zero explainability |

**Winning Feature #1: Hybrid Graph + Vector Matching**

| | Vector-Only (competitors) | RAX (Hybrid) |
|---|---|---|
| Find similar resumes | ✅ | ✅ (Qdrant) |
| Explain WHY it matches | ❌ | ✅ (Neo4j paths) |
| Skill taxonomy | ❌ | ✅ (hierarchical graph) |
| Multi-hop reasoning | ❌ | ✅ |
| Bias audit trail | ❌ | ✅ (queryable) |
| Self-improving | ❌ | ✅ (auto-enriching) |

**Score Fusion:**
`hybrid = 0.30×semantic(Qdrant) + 0.50×structural(Neo4j) + 0.15×experience + 0.05×education`

---

## SLIDE 3 — Winning Features #2 & #3

**Feature #2: Full Explainability**
- Skill match: "4/5 must-have skills matched: Python ✅, SQL ✅, AWS ✅, Docker ✅, K8s ❌"
- Experience depth: "8 years Python (needs 5) — surplus; 0 years K8s (needs 2) — gap"
- AI narrative: natural language explanation per candidate
- Radar chart: visual skills/experience/education scoring
- Bias audit: graph query proves no protected attributes influenced score

**Feature #3: Bias-Aware Screening by Design**
- Anonymization runs BEFORE scoring — not optional
- Names → `[CANDIDATE_ID]`, Universities → `[UNIVERSITY]`
- Gender/nationality signals removed
- "Reveal Identity" toggle — conscious choice after reviewing scores
- Compliant: EEOC, DEI mandates, EU AI Act

---

## SLIDE 4 — Winning Feature #4 & Workflow

**Feature #4: Real-Time Multi-Agent Pipeline**
```
Resume Upload → Parsing ✅ → Bias Filter ✅ → Graph + Vector (parallel) ✅ → Hybrid Match ✅ → Scoring ✅
```
- Live WebSocket cards per resume — watch each stage animate
- Multiple resumes process concurrently
- Parallel graph/vector execution saves ~30% pipeline time
- Failures are visible immediately — no silent rejections

**Recruiter Workflow:**
```
Login → Create Job → Upload Resumes (bulk)
  → Watch Live Processing (WebSocket)
    → Review Ranked Candidates
      → View Detail (radar chart, strengths/gaps)
      → Reveal Identity (after scoring)
      → Generate Feedback → Send
```

---

## SLIDE 5 — System Architecture

```
         [React Frontend — Vercel]
                  │ REST + WS
         [FastAPI Backend — Railway]
                  │
    ┌─────────────┼─────────────┐
    │             │             │
[Supabase]    [Neo4j]      [Qdrant]      [Gemini API]
PostgreSQL   Knowledge     Vector DB      gemini-1.5-pro
+ Storage    Graph         Embeddings     text-embed-004
```

**Agent Pipeline:**
```
ResumeParser → BiasFilter → [GraphIngestion ║ Embedding] → HybridMatch → Scoring
                                                                          ↓
                                                        FeedbackAgent (on demand)
```

**Tech Stack:**

| | Technology |
|---|---|
| Frontend | React + TypeScript + Tailwind + shadcn/ui |
| Backend | Python FastAPI (async) |
| Database | Supabase (PostgreSQL) |
| Graph DB | Neo4j (AuraDB free) |
| Vector DB | Qdrant (Cloud free) |
| AI/LLM | Google Gemini |
| Real-Time | WebSocket |
| Deploy | Vercel · Railway · AuraDB · Qdrant Cloud |

**Distributed Computing:** Parallel agents · Async pipeline · Stateless JWT scaling · Self-enriching graph · Event-driven WebSocket · Cloud-native (zero local disk)

---

## SLIDE 6 — Conclusion & Implementation Plan

**Why RAX Wins:**
- ✅ Hybrid graph + vector matching (no competitor has both)
- ✅ Full explainability (graph paths, not black-box scores)
- ✅ Bias anonymization by design (not an add-on)
- ✅ Real-time processing visibility
- ✅ Self-enriching skill taxonomy
- ✅ $0 infrastructure (all free-tier)

**Implementation Timeline:**

| Phase | Scope | When |
|---|---|---|
| 0 | Scaffold + Docker + Supabase | Week 1 |
| 1 | Backend: API + Auth + DB | Weeks 2–3 |
| 2 | AI Pipeline: 6 agents | Weeks 2–4 |
| 3 | WebSocket real-time | Week 4 |
| 4 | Frontend: all screens | Weeks 2–5 |
| 5 | Cloud deployment | Week 5 |
| 6 | Integration testing | Week 6 |

**Milestones:** W1: Infra ready → W3: API live → W4: Pipeline works → W5: Full UI → W6: Deployed

**Risks Handled:** Gemini rate limits (retry + cache) · Neo4j node limits (dedup) · Sparse graph (vector compensates) · WebSocket drops (auto-reconnect)

> **RAX: The first hiring platform that combines structural reasoning with semantic discovery. Auditable. Bias-free. Real-time. Ready to build.**

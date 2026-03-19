# RAX — System Architecture Diagrams for Eraser.io

> Copy each code block into [eraser.io](https://app.eraser.io/) → "New Diagram" → paste code → render.
> Select **"Cloud Architecture"** diagram type in Eraser.io before pasting.

---

## Diagram 1: High-Level Four-Tier System Architecture

```
// RAX — Resume Analysis eXpert | Four-Tier Cloud Architecture

// ===== CLIENT TIER =====
Client Tier [color: blue] {
  React Frontend [icon: react, label: "React + TypeScript (Vite)"] {
    Auth Pages [icon: lock]
    Job Management [icon: clipboard]
    Resume Upload + Live WS [icon: upload-cloud]
    Candidate Dashboard [icon: bar-chart-2]
    Feedback View [icon: message-square]
  }
  Zustand State [icon: database, label: "Zustand State Mgmt"]
  Tailwind + shadcn/ui [icon: layout, label: "Tailwind + shadcn/ui"]
  Vercel [icon: vercel, label: "Deployed on Vercel"]
}

// ===== SERVER TIER =====
Server Tier [color: green] {
  FastAPI Backend [icon: python, label: "Python FastAPI (Async)"] {
    Auth Routes [icon: shield]
    Jobs API [icon: briefcase]
    Resumes API [icon: file-text]
    WebSocket Endpoint [icon: radio]
  }

  Pipeline Orchestrator [icon: git-merge, label: "Pipeline Orchestrator"] {
    ResumeParserAgent [icon: file-search, label: "1. ResumeParser Agent"]
    BiasFilterAgent [icon: eye-off, label: "2. BiasFilter Agent"]
    GraphIngestionAgent [icon: share-2, label: "3a. GraphIngestion Agent"]
    EmbeddingAgent [icon: cpu, label: "3b. Embedding Agent"]
    HybridMatchingAgent [icon: git-pull-request, label: "4. HybridMatching Agent"]
    ScoringAgent [icon: award, label: "5. Scoring Agent"]
    FeedbackAgent [icon: message-circle, label: "6. Feedback Agent (On Demand)"]
  }

  JWT Auth [icon: key, label: "JWT Auth (python-jose)"]
  Alembic [icon: layers, label: "Alembic Migrations"]
  Railway [icon: cloud, label: "Deployed on Railway / Render"]
}

// ===== DATA TIER =====
Data Tier [color: orange] {
  Supabase [icon: database, label: "Supabase (PostgreSQL)"] {
    Users Table [icon: users]
    Jobs Table [icon: briefcase]
    Resumes Table [icon: file]
    Analyses Table [icon: activity]
    Feedback Table [icon: message-square]
  }
  Supabase Storage [icon: hard-drive, label: "Supabase Storage (Resume Files)"]
}

// ===== GRAPH TIER =====
Graph Tier [color: purple] {
  Neo4j [icon: share-2, label: "Neo4j (AuraDB / Docker)"] {
    Candidate Nodes [icon: user]
    Skill Nodes [icon: tool]
    Company Nodes [icon: building]
    Role Nodes [icon: tag]
    Education Nodes [icon: book]
    SkillCluster Nodes [icon: layers]
  }
}

// ===== VECTOR TIER =====
Vector Tier [color: pink] {
  Qdrant [icon: search, label: "Qdrant (Vector DB)"] {
    Resumes Collection [icon: file-text, label: "resumes collection"]
    Job Descriptions Collection [icon: briefcase, label: "job_descs collection"]
  }
}

// ===== AI TIER =====
AI Tier [color: red] {
  Gemini API [icon: zap, label: "Google Gemini API"] {
    gemini-1.5-pro [icon: cpu, label: "gemini-1.5-pro (Parse, Score, Feedback)"]
    text-embedding-004 [icon: hash, label: "text-embedding-004 (768-dim Vectors)"]
  }
}

// ===== CONNECTIONS =====
// Client to Server
React Frontend > FastAPI Backend: REST API (Axios)
React Frontend <> WebSocket Endpoint: WebSocket (Live Updates)

// Server to Data
FastAPI Backend > Supabase: SQL Queries
Resumes API > Supabase Storage: Upload / Retrieve Files
Alembic > Supabase: Schema Migrations

// Pipeline Internal Flow
ResumeParserAgent > BiasFilterAgent: Structured JSON
BiasFilterAgent > GraphIngestionAgent: Anonymized Resume
BiasFilterAgent > EmbeddingAgent: Anonymized Resume
GraphIngestionAgent > HybridMatchingAgent: Graph Entities Ready
EmbeddingAgent > HybridMatchingAgent: Vectors Stored
HybridMatchingAgent > ScoringAgent: Hybrid Score Context

// Server to Graph
GraphIngestionAgent > Neo4j: Ingest Nodes + Relationships
HybridMatchingAgent > Neo4j: Cypher Graph Traversal

// Server to Vector
EmbeddingAgent > Qdrant: Store Embeddings
HybridMatchingAgent > Qdrant: Cosine Similarity Search

// Server to AI
ResumeParserAgent > Gemini API: Extract Structured Data
ScoringAgent > Gemini API: Generate Scores + Explanation
FeedbackAgent > Gemini API: Generate Candidate Feedback
EmbeddingAgent > text-embedding-004: Generate 768-dim Vectors

// Pipeline Status to Client
ScoringAgent > WebSocket Endpoint: Push Results
Pipeline Orchestrator > WebSocket Endpoint: Stage Status Updates
```

---

## Diagram 2: AI Pipeline Flow (Sequence Diagram)

> In Eraser.io select **"Sequence Diagram"** diagram type.

```
// RAX — AI Pipeline Sequence Diagram

title RAX — Multi-Agent AI Pipeline Flow

Recruiter [icon: user, color: blue]
Frontend [icon: monitor, color: blue]
FastAPI [icon: server, color: green]
Orchestrator [icon: git-merge, color: green]
ResumeParser [icon: file-search, color: green]
BiasFilter [icon: eye-off, color: green]
GraphIngestion [icon: share-2, color: purple]
Embedding [icon: cpu, color: pink]
HybridMatcher [icon: git-pull-request, color: green]
Scorer [icon: award, color: green]
Neo4j [icon: share-2, color: purple]
Qdrant [icon: search, color: pink]
Gemini [icon: zap, color: red]
Supabase [icon: database, color: orange]
WebSocket [icon: radio, color: blue]

// Upload Flow
Recruiter > Frontend: Upload Resumes (PDF/DOCX)
Frontend > FastAPI: POST /api/resumes (multipart)
FastAPI > Supabase: Store file in Supabase Storage
FastAPI > Orchestrator: Trigger pipeline

// Stage 1: Parse
Orchestrator > ResumeParser: Extract text
ResumeParser > Gemini: Send raw text
Gemini > ResumeParser: Structured JSON (skills, exp, edu)
Orchestrator > WebSocket: Status: "parsing complete"
WebSocket > Frontend: Push stage update

// Stage 2: Bias Filter
Orchestrator > BiasFilter: Anonymize resume
BiasFilter > BiasFilter: Remove name, gender, institution
Orchestrator > WebSocket: Status: "bias filtering complete"
WebSocket > Frontend: Push stage update

// Stage 3a & 3b: Parallel Execution
par {
  // Graph Ingestion
  Orchestrator > GraphIngestion: Ingest into graph
  GraphIngestion > Neo4j: CREATE nodes (Candidate, Skill, Company, Role, Education)
  GraphIngestion > Neo4j: CREATE relationships (HAS_SKILL, WORKED_AT, HAS_DEGREE)
  Neo4j > GraphIngestion: Confirm ingestion

  // Vector Embedding
  Orchestrator > Embedding: Embed resume
  Embedding > Gemini: text-embedding-004
  Gemini > Embedding: 768-dim vector
  Embedding > Qdrant: Upsert vector to resumes collection
  Qdrant > Embedding: Confirm storage
}
Orchestrator > WebSocket: Status: "ingestion + embedding complete"
WebSocket > Frontend: Push stage update

// Stage 4: Hybrid Matching
Orchestrator > HybridMatcher: Compute hybrid score
HybridMatcher > Neo4j: Cypher query (structural skill match)
Neo4j > HybridMatcher: Graph traversal paths + structural score
HybridMatcher > Qdrant: Cosine similarity query
Qdrant > HybridMatcher: Semantic similarity score
HybridMatcher > HybridMatcher: Fuse scores (0.30×semantic + 0.50×structural + 0.15×exp + 0.05×edu)
Orchestrator > WebSocket: Status: "matching complete"
WebSocket > Frontend: Push stage update

// Stage 5: Scoring
Orchestrator > Scorer: Generate explainable scores
Scorer > Gemini: Hybrid context + prompt → scores + explanation
Gemini > Scorer: Multi-dim scores (overall, skills, exp, edu) + natural language explanation
Scorer > Supabase: Store analysis record
Orchestrator > WebSocket: Status: "scoring complete"
WebSocket > Frontend: Push final results + ranked candidate

// Optional: Feedback
Recruiter > Frontend: Click "Generate Feedback"
Frontend > FastAPI: POST /api/feedback
FastAPI > Gemini: Generate constructive feedback
Gemini > FastAPI: 150-200 word feedback text
FastAPI > Supabase: Store feedback
FastAPI > Frontend: Return feedback content
```

---

## Diagram 3: Entity Relationship / Data Model

> In Eraser.io select **"Entity Relationship"** diagram type.

```
// RAX — Data Model (Entity Relationship Diagram)

users [icon: users, color: blue] {
  id string pk
  email string unique
  hashed_password string
  full_name string
  role enum "recruiter, hiring_manager"
  created_at timestamp
}

jobs [icon: briefcase, color: green] {
  id string pk
  title string
  description text
  requirements text
  status enum "draft, active, closed"
  created_by string fk
  qdrant_embed_id string
  neo4j_node_id string
  created_at timestamp
}

candidates [icon: user, color: orange] {
  id string pk
  name string
  email string
  phone string
  neo4j_node_id string
  created_at timestamp
}

resumes [icon: file-text, color: purple] {
  id string pk
  job_id string fk
  candidate_id string fk
  file_path string
  raw_text text
  parsed_json jsonb
  anonymized_json jsonb
  qdrant_embed_id string
  pipeline_status enum "uploaded, parsing, filtering, ingesting, embedding, matching, scoring, completed, failed"
  created_at timestamp
}

analyses [icon: activity, color: red] {
  id string pk
  resume_id string fk
  job_id string fk
  overall_score float
  skills_score float
  experience_score float
  education_score float
  semantic_similarity float
  structural_match float
  explanation text
  strengths jsonb
  gaps jsonb
  graph_paths jsonb
  created_at timestamp
}

feedback [icon: message-square, color: pink] {
  id string pk
  job_id string fk
  candidate_id string fk
  resume_id string fk
  content text
  sent_at timestamp
  created_at timestamp
}

// Relationships
users.id <> jobs.created_by
jobs.id <> resumes.job_id
candidates.id <> resumes.candidate_id
resumes.id <> analyses.resume_id
jobs.id <> analyses.job_id
jobs.id <> feedback.job_id
candidates.id <> feedback.candidate_id
resumes.id <> feedback.resume_id
```

---

## Diagram 4: Neo4j Knowledge Graph Schema

> In Eraser.io select **"Cloud Architecture"** or **"Flowchart"** diagram type.

```
// RAX — Neo4j Knowledge Graph Schema

// Nodes
Candidate [icon: user, color: blue]
Skill [icon: tool, color: green]
SkillCluster [icon: layers, color: green]
Company [icon: building, color: orange]
Role [icon: tag, color: purple]
Education [icon: book, color: red]
Institution [icon: home, color: red]
Job [icon: briefcase, color: yellow]

// Candidate Relationships
Candidate > Skill: HAS_SKILL {years, proficiency}
Candidate > Company: WORKED_AT {duration, start, end}
Candidate > Role: HELD_ROLE {title}
Candidate > Education: HAS_DEGREE {level, field}
Candidate > Institution: STUDIED_AT

// Job Relationships
Job > Skill: REQUIRES_SKILL {priority, min_years}
Job > Education: REQUIRES_DEGREE {min_level}

// Skill Taxonomy
Skill > SkillCluster: BELONGS_TO
Skill > Skill: IS_SIMILAR_TO {score}

// Examples
Python [icon: code, color: green, label: "Python"]
Programming Languages [icon: layers, color: green, label: "Programming Languages"]
Technical Skills [icon: layers, color: green, label: "Technical Skills"]

Python > Programming Languages: BELONGS_TO
Programming Languages > Technical Skills: BELONGS_TO

React [icon: code, color: green, label: "React"]
React > Python: IS_SIMILAR_TO {score: 0.31}

Django [icon: code, color: green, label: "Django"]
Django > Python: IS_SIMILAR_TO {score: 0.89}
```

---

## Diagram 5: Deployment Architecture

> In Eraser.io select **"Cloud Architecture"** diagram type.

```
// RAX — Deployment Architecture (All Free-Tier Cloud)

// ===== USER =====
Recruiter [icon: user, color: blue]
Hiring Manager [icon: users, color: blue]

// ===== FRONTEND HOSTING =====
Vercel [icon: vercel, color: black] {
  React SPA [icon: react, label: "React + TypeScript + Vite"]
  Static Assets [icon: image, label: "Tailwind CSS + shadcn/ui"]
  CDN Edge [icon: globe, label: "Vercel Edge CDN"]
}

// ===== BACKEND HOSTING =====
Railway [icon: cloud, color: green] {
  FastAPI Instance [icon: python, label: "FastAPI (Async)"]
  Pipeline Workers [icon: cpu, label: "Background Task Workers"]
  WebSocket Server [icon: radio, label: "WebSocket Server"]
}

// ===== MANAGED DATABASES =====
Supabase Cloud [icon: database, color: orange] {
  PostgreSQL [icon: database, label: "PostgreSQL (Managed)"]
  File Storage [icon: hard-drive, label: "S3-Compatible Storage"]
  Auth Helpers [icon: shield, label: "Connection Pooling (pgBouncer)"]
}

Neo4j AuraDB [icon: share-2, color: purple] {
  Knowledge Graph [icon: share-2, label: "Knowledge Graph (Free Tier)"]
  APOC Plugins [icon: tool, label: "APOC + GDS"]
}

Qdrant Cloud [icon: search, color: pink] {
  Vector Index [icon: search, label: "Vector Index (1GB Free)"]
  REST API [icon: globe, label: "REST + gRPC"]
}

// ===== EXTERNAL APIs =====
Google Cloud [icon: gcp, color: red] {
  Gemini Pro [icon: zap, label: "gemini-1.5-pro"]
  Embedding API [icon: hash, label: "text-embedding-004"]
}

// ===== CONNECTIONS =====
Recruiter > Vercel: HTTPS
Hiring Manager > Vercel: HTTPS
Vercel > Railway: REST API + WebSocket
Railway > Supabase Cloud: SQL + File Upload
Railway > Neo4j AuraDB: Bolt Protocol (neo4j+s://)
Railway > Qdrant Cloud: REST / gRPC
Railway > Google Cloud: HTTPS (Gemini API)
```

---

## Diagram 6: Recruiter Workflow (Flowchart)

> In Eraser.io select **"Flowchart"** diagram type.

```
// RAX — End-to-End Recruiter Workflow

Start [shape: oval, label: "Recruiter Logs In"]
CreateJob [shape: rectangle, label: "Create Job Posting (Title + JD)"]
JDProcess [shape: rectangle, label: "JD embedded in Qdrant + decomposed into Neo4j"]
UploadResumes [shape: rectangle, label: "Upload Resumes (Bulk Drag & Drop)"]
PipelineTrigger [shape: rectangle, label: "Pipeline Orchestrator Triggered"]

// Pipeline Stages
Parsing [shape: rectangle, label: "1. ResumeParser: Extract → Structured JSON"]
BiasFilter [shape: rectangle, label: "2. BiasFilter: Anonymize PII"]
ParallelStart [shape: diamond, label: "Parallel Execution"]
GraphIngest [shape: rectangle, label: "3a. GraphIngestion → Neo4j"]
VectorEmbed [shape: rectangle, label: "3b. Embedding → Qdrant"]
ParallelEnd [shape: diamond, label: "Sync"]
HybridMatch [shape: rectangle, label: "4. HybridMatching: Graph + Vector Fusion"]
Scoring [shape: rectangle, label: "5. Scoring: Multi-dim Scores + Explanation"]
Complete [shape: rectangle, label: "Results Stored + WebSocket Push"]

// Review
WatchLive [shape: rectangle, label: "Watch Live Processing (WebSocket Cards)"]
ReviewCandidates [shape: rectangle, label: "Review Ranked Candidate List"]
Decision [shape: diamond, label: "Action?"]
ViewDetail [shape: rectangle, label: "View Detail: Radar Chart + Strengths/Gaps + AI Explanation"]
RevealIdentity [shape: rectangle, label: "Reveal Identity (After Scoring)"]
GenerateFeedback [shape: rectangle, label: "Generate AI Feedback"]
SendFeedback [shape: rectangle, label: "Send Feedback (Copy / Mark Sent)"]
End [shape: oval, label: "Done"]

// Flow
Start > CreateJob
CreateJob > JDProcess
JDProcess > UploadResumes
UploadResumes > PipelineTrigger
PipelineTrigger > Parsing
Parsing > BiasFilter
BiasFilter > ParallelStart
ParallelStart > GraphIngest: Branch A
ParallelStart > VectorEmbed: Branch B
GraphIngest > ParallelEnd
VectorEmbed > ParallelEnd
ParallelEnd > HybridMatch
HybridMatch > Scoring
Scoring > Complete
Complete > WatchLive
WatchLive > ReviewCandidates
ReviewCandidates > Decision
Decision > ViewDetail: View Detail
Decision > RevealIdentity: Reveal Identity
Decision > GenerateFeedback: Generate Feedback
ViewDetail > ReviewCandidates
RevealIdentity > ReviewCandidates
GenerateFeedback > SendFeedback
SendFeedback > End
```

---

## Quick Start Guide

1. Go to [app.eraser.io](https://app.eraser.io/)
2. Click **"+ New"** → **"Diagram"**
3. Select the diagram type noted above each code block
4. Paste the code block content (without the triple backtick markers)
5. The diagram will render automatically

### Diagram Type Reference

| Diagram | Eraser.io Type |
|---|---|
| Diagram 1: Four-Tier Architecture | Cloud Architecture |
| Diagram 2: AI Pipeline Flow | Sequence Diagram |
| Diagram 3: Data Model | Entity Relationship |
| Diagram 4: Neo4j Graph Schema | Cloud Architecture / Flowchart |
| Diagram 5: Deployment Architecture | Cloud Architecture |
| Diagram 6: Recruiter Workflow | Flowchart |

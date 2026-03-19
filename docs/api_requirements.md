# RAX — Backend API & Database Requirements Document

> **Purpose:** This document defines every API endpoint, WebSocket channel, request/response schema, database table, and integration contract that the backend (Person 1) and AI pipeline (Person 2) must implement for the frontend to be fully functional.
>
> **Audience:** Backend developer (FastAPI + Supabase) and AI pipeline developer (Gemini + Neo4j + Qdrant)
>
> **Date:** March 2026

---

## Table of Contents

1. [API Design Conventions](#1-api-design-conventions)
2. [Authentication APIs](#2-authentication-apis)
3. [Job Management APIs](#3-job-management-apis)
4. [Resume Upload & Pipeline APIs](#4-resume-upload--pipeline-apis)
5. [Candidate & Analysis APIs](#5-candidate--analysis-apis)
6. [Feedback APIs](#6-feedback-apis)
7. [Dashboard APIs](#7-dashboard-apis)
8. [WebSocket Contract](#8-websocket-contract)
9. [Database Schema (Supabase PostgreSQL)](#9-database-schema-supabase-postgresql)
10. [Knowledge Graph Schema (Neo4j)](#10-knowledge-graph-schema-neo4j)
11. [Vector Store Schema (Qdrant)](#11-vector-store-schema-qdrant)
12. [Error Handling Contract](#12-error-handling-contract)
13. [Environment Variables](#13-environment-variables)
14. [Integration Sequence Diagrams](#14-integration-sequence-diagrams)

---

## 1. API Design Conventions

| Convention | Value |
|---|---|
| Base URL | `{BACKEND_URL}/api/v1` |
| Content-Type | `application/json` (except file uploads: `multipart/form-data`) |
| Auth Header | `Authorization: Bearer <jwt_token>` |
| Pagination | `?page=1&page_size=20` (default page_size=20, max=100) |
| Sorting | `?sort_by=field&order=asc|desc` |
| Date Format | ISO 8601 (`2026-03-20T14:30:00Z`) |
| ID Format | UUID v4 |
| HTTP Status Codes | 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error, 500 Internal Error |

### Standard Envelope Response

```json
{
  "success": true,
  "data": { ... },
  "message": "optional human-readable message"
}
```

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [ ... ]
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 85,
    "total_pages": 5
  }
}
```

---

## 2. Authentication APIs

**Owner:** Person 1 (Backend Core)

### 2.1 `POST /api/v1/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "recruiter@company.com",
  "password": "SecureP@ss123",
  "full_name": "Jane Smith",
  "role": "recruiter"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `email` | string | yes | Valid email format, unique |
| `password` | string | yes | Min 8 chars, 1 uppercase, 1 number, 1 special |
| `full_name` | string | yes | 2–100 chars |
| `role` | string | yes | Enum: `recruiter`, `hiring_manager` |

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "recruiter@company.com",
    "full_name": "Jane Smith",
    "role": "recruiter",
    "created_at": "2026-03-20T14:30:00Z"
  },
  "message": "Account created successfully"
}
```

**Errors:**
| Code | When |
|---|---|
| 409 Conflict | Email already registered |
| 422 Unprocessable | Validation failure (weak password, invalid email, etc.) |

---

### 2.2 `POST /api/v1/auth/login`

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "recruiter@company.com",
  "password": "SecureP@ss123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "uuid",
      "email": "recruiter@company.com",
      "full_name": "Jane Smith",
      "role": "recruiter"
    }
  }
}
```

**Errors:**
| Code | When |
|---|---|
| 401 Unauthorized | Invalid email or password |

---

### 2.3 `GET /api/v1/auth/me`

Get current authenticated user profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "recruiter@company.com",
    "full_name": "Jane Smith",
    "role": "recruiter",
    "created_at": "2026-03-20T14:30:00Z"
  }
}
```

---

### 2.4 `PUT /api/v1/auth/me`

Update current user profile (name, password).

**Request Body:**
```json
{
  "full_name": "Jane Doe",
  "current_password": "OldP@ss123",
  "new_password": "NewP@ss456"
}
```

All fields optional. `current_password` required only when changing password.

**Response (200 OK):** Updated user object.

---

## 3. Job Management APIs

**Owner:** Person 1 (Backend Core) — job creation triggers Person 2's JD embedding + graph ingestion

### 3.1 `POST /api/v1/jobs`

Create a new job posting. **Side effect:** Backend triggers `EmbeddingAgent` (JD → Qdrant) and `GraphIngestionAgent` (JD → Neo4j `REQUIRES_SKILL`, `REQUIRES_DEGREE`) as a background task.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Senior Full-Stack Engineer",
  "description": "We are looking for an experienced full-stack engineer...",
  "requirements": [
    { "skill": "React", "priority": "must-have", "min_years": 3 },
    { "skill": "Python", "priority": "must-have", "min_years": 4 },
    { "skill": "PostgreSQL", "priority": "must-have", "min_years": 2 },
    { "skill": "Docker", "priority": "nice-to-have", "min_years": 1 },
    { "skill": "Kubernetes", "priority": "nice-to-have", "min_years": 1 }
  ],
  "education": {
    "min_level": "bachelor",
    "preferred_field": "Computer Science"
  },
  "experience_years": 5,
  "location": "Remote",
  "salary_range": { "min": 120000, "max": 180000, "currency": "USD" },
  "scoring_weights": {
    "structural": 0.50,
    "semantic": 0.30,
    "experience": 0.15,
    "education": 0.05
  }
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | 5–200 chars |
| `description` | string | yes | Rich text, 50–10000 chars |
| `requirements` | array | yes | At least 1 skill required |
| `requirements[].skill` | string | yes | Skill name |
| `requirements[].priority` | string | yes | Enum: `must-have`, `nice-to-have` |
| `requirements[].min_years` | number | no | Default 0 |
| `education` | object | no | |
| `education.min_level` | string | no | Enum: `high_school`, `associate`, `bachelor`, `master`, `phd` |
| `education.preferred_field` | string | no | |
| `experience_years` | number | no | Overall years of experience |
| `location` | string | no | |
| `salary_range` | object | no | |
| `scoring_weights` | object | no | Must sum to 1.0; defaults to 0.50/0.30/0.15/0.05 |

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Senior Full-Stack Engineer",
    "description": "...",
    "requirements": [ ... ],
    "education": { ... },
    "experience_years": 5,
    "location": "Remote",
    "salary_range": { ... },
    "scoring_weights": { ... },
    "status": "active",
    "embedding_status": "processing",
    "created_by": "uuid",
    "created_at": "2026-03-20T14:30:00Z",
    "candidate_count": 0
  }
}
```

---

### 3.2 `GET /api/v1/jobs`

List all jobs created by the current user.

**Query Params:**
| Param | Type | Default | Notes |
|---|---|---|---|
| `page` | int | 1 | |
| `page_size` | int | 20 | Max 100 |
| `status` | string | all | Filter: `active`, `closed`, `draft` |
| `search` | string | — | Search in title/description |
| `sort_by` | string | `created_at` | `created_at`, `title`, `candidate_count` |
| `order` | string | `desc` | `asc`, `desc` |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Senior Full-Stack Engineer",
      "status": "active",
      "candidate_count": 42,
      "avg_score": 72.5,
      "created_at": "2026-03-20T14:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 5, "total_pages": 1 }
}
```

---

### 3.3 `GET /api/v1/jobs/{job_id}`

Get full job details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Senior Full-Stack Engineer",
    "description": "Full rich text...",
    "requirements": [
      { "skill": "React", "priority": "must-have", "min_years": 3 }
    ],
    "education": { "min_level": "bachelor", "preferred_field": "Computer Science" },
    "experience_years": 5,
    "location": "Remote",
    "salary_range": { "min": 120000, "max": 180000, "currency": "USD" },
    "scoring_weights": { "structural": 0.50, "semantic": 0.30, "experience": 0.15, "education": 0.05 },
    "status": "active",
    "embedding_status": "completed",
    "created_by": "uuid",
    "created_at": "2026-03-20T14:30:00Z",
    "updated_at": "2026-03-20T14:35:00Z",
    "candidate_count": 42,
    "avg_score": 72.5,
    "top_score": 94.2
  }
}
```

---

### 3.4 `PUT /api/v1/jobs/{job_id}`

Update a job posting. **Side effect:** If `description` or `requirements` change, re-triggers embedding + graph ingestion.

**Request Body:** Same shape as POST, all fields optional.

**Response (200 OK):** Updated job object.

---

### 3.5 `PATCH /api/v1/jobs/{job_id}/status`

Change job status (active, closed, draft).

**Request Body:**
```json
{
  "status": "closed"
}
```

**Response (200 OK):** Updated job object.

---

### 3.6 `DELETE /api/v1/jobs/{job_id}`

Delete a job and all associated resumes, analyses, feedback.

**Response (204 No Content)**

---

## 4. Resume Upload & Pipeline APIs

**Owner:** Person 1 (route + file storage) + Person 2 (pipeline orchestration)

### 4.1 `POST /api/v1/jobs/{job_id}/resumes`

Bulk upload resumes for a specific job. **Side effect:** Triggers `PipelineOrchestrator` as a background task for each resume. WebSocket events emitted per stage.

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body (form-data):**
| Field | Type | Required | Notes |
|---|---|---|---|
| `files` | File[] | yes | Multiple files, each PDF or DOCX, max 10MB per file, max 50 files per request |

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "uploaded": [
      {
        "resume_id": "uuid",
        "candidate_id": "uuid",
        "filename": "john_doe_resume.pdf",
        "status": "queued",
        "file_size": 245760
      },
      {
        "resume_id": "uuid",
        "candidate_id": "uuid",
        "filename": "jane_smith_resume.docx",
        "status": "queued",
        "file_size": 189440
      }
    ],
    "total_queued": 2
  },
  "message": "2 resumes queued for processing"
}
```

**Errors:**
| Code | When |
|---|---|
| 400 Bad Request | No files provided, unsupported format |
| 413 Payload Too Large | File exceeds 10MB or batch exceeds 50 files |
| 404 Not Found | Job doesn't exist |

---

### 4.2 `GET /api/v1/jobs/{job_id}/resumes`

List all resumes uploaded for a job with their processing status.

**Query Params:**
| Param | Type | Default | Notes |
|---|---|---|---|
| `status` | string | all | `queued`, `processing`, `completed`, `failed` |
| `page` | int | 1 | |
| `page_size` | int | 20 | |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "resume_id": "uuid",
      "candidate_id": "uuid",
      "filename": "john_doe_resume.pdf",
      "status": "completed",
      "pipeline_stage": "completed",
      "overall_score": 89.0,
      "uploaded_at": "2026-03-20T14:30:00Z",
      "processed_at": "2026-03-20T14:30:45Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 4.3 `GET /api/v1/resumes/{resume_id}`

Get detailed resume info including parsed data and raw text.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "candidate_id": "uuid",
    "job_id": "uuid",
    "filename": "john_doe_resume.pdf",
    "file_url": "https://supabase.storage/...",
    "raw_text": "John Doe\nSenior Software Engineer...",
    "parsed_data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "skills": [
        { "name": "Python", "years": 8, "proficiency": "expert" },
        { "name": "React", "years": 5, "proficiency": "advanced" }
      ],
      "experience": [
        {
          "company": "TechCorp",
          "role": "Senior Software Engineer",
          "start": "2020-01",
          "end": "present",
          "duration_years": 6,
          "description": "Led team of 5..."
        }
      ],
      "education": [
        {
          "degree": "Master of Science",
          "field": "Computer Science",
          "institution": "MIT",
          "year": 2018
        }
      ]
    },
    "status": "completed",
    "pipeline_stage": "completed",
    "uploaded_at": "2026-03-20T14:30:00Z",
    "processed_at": "2026-03-20T14:30:45Z"
  }
}
```

---

### 4.4 `GET /api/v1/resumes/{resume_id}/download`

Download original resume file.

**Response:** Binary file stream with appropriate `Content-Type` and `Content-Disposition` headers.

---

## 5. Candidate & Analysis APIs

**Owner:** Person 1 (routes + DB queries) + Person 2 (analysis data)

### 5.1 `GET /api/v1/jobs/{job_id}/candidates`

Get ranked candidate list for a job — **the primary screening view**.

**Query Params:**
| Param | Type | Default | Notes |
|---|---|---|---|
| `page` | int | 1 | |
| `page_size` | int | 20 | |
| `sort_by` | string | `overall_score` | `overall_score`, `skills_score`, `experience_score`, `education_score`, `semantic_score` |
| `order` | string | `desc` | `asc`, `desc` |
| `min_score` | float | 0 | Filter: minimum overall score (0–100) |
| `max_score` | float | 100 | Filter: maximum overall score |
| `status` | string | `completed` | `completed`, `processing`, `failed` |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "candidate_id": "uuid",
      "resume_id": "uuid",
      "anonymized_name": "[CANDIDATE_42]",
      "real_name": "John Doe",
      "identity_revealed": false,
      "overall_score": 89.0,
      "skills_score": 94.4,
      "semantic_score": 86.0,
      "experience_score": 73.4,
      "education_score": 100.0,
      "top_skills": ["Python", "React", "PostgreSQL"],
      "status": "completed",
      "processed_at": "2026-03-20T14:30:45Z"
    }
  ],
  "pagination": { ... }
}
```

**Key notes for frontend:**
- `anonymized_name` always returned; `real_name` only populated when `identity_revealed` is true
- The frontend has a "Reveal Identity" toggle per candidate — calls `PATCH` (see 5.3)
- `top_skills` is a convenience array (top 3–5 matched skills) for display in the list view

---

### 5.2 `GET /api/v1/candidates/{candidate_id}/analysis?job_id={job_id}`

Get the full analysis for a candidate-job pair — **the detail view**.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "candidate_id": "uuid",
    "resume_id": "uuid",
    "job_id": "uuid",
    "anonymized_name": "[CANDIDATE_42]",
    "real_name": null,
    "identity_revealed": false,

    "scores": {
      "overall": 89.0,
      "structural_skill_match": 94.4,
      "semantic_similarity": 86.0,
      "experience_match": 73.4,
      "education_match": 100.0
    },

    "scoring_weights": {
      "structural": 0.50,
      "semantic": 0.30,
      "experience": 0.15,
      "education": 0.05
    },

    "skill_matches": [
      {
        "required_skill": "Python",
        "candidate_skill": "Python",
        "match_type": "direct",
        "credit": 1.0,
        "candidate_years": 8,
        "required_years": 5,
        "priority": "must-have"
      },
      {
        "required_skill": "Kubernetes",
        "candidate_skill": "Docker",
        "match_type": "similar",
        "similarity_score": 0.72,
        "credit": 0.72,
        "candidate_years": 2,
        "required_years": 2,
        "priority": "nice-to-have"
      }
    ],

    "strengths": [
      "Strong Python expertise (8 years vs. 5 required)",
      "Comprehensive full-stack experience with React and PostgreSQL",
      "Master's degree exceeds Bachelor's requirement"
    ],

    "gaps": [
      "No direct Kubernetes experience — related Docker experience provides partial match (72%)",
      "Docker experience slightly below requirement (2 years vs. 3 required)"
    ],

    "explanation": "This candidate demonstrates strong alignment with the Senior Full-Stack Engineer role. They bring extensive Python expertise and solid React/PostgreSQL foundations that directly match core requirements. The knowledge graph reveals a partial Kubernetes match through their Docker experience (72% similarity). Their Master's in Computer Science exceeds the Bachelor's requirement. The primary gap is limited container orchestration experience, though their Docker background provides a strong foundation for Kubernetes adoption.",

    "education": {
      "candidate_level": "master",
      "candidate_field": "Computer Science",
      "required_level": "bachelor",
      "score": 1.0
    },

    "experience_summary": {
      "total_years": 10,
      "relevant_roles": [
        {
          "company": "[COMPANY]",
          "role": "Senior Software Engineer",
          "duration_years": 6
        }
      ]
    },

    "parsed_skills": [
      { "name": "Python", "years": 8, "proficiency": "expert" },
      { "name": "React", "years": 5, "proficiency": "advanced" },
      { "name": "PostgreSQL", "years": 5, "proficiency": "advanced" },
      { "name": "Docker", "years": 2, "proficiency": "intermediate" },
      { "name": "AWS", "years": 3, "proficiency": "intermediate" }
    ],

    "feedback_generated": false,
    "processed_at": "2026-03-20T14:30:45Z"
  }
}
```

---

### 5.3 `PATCH /api/v1/candidates/{candidate_id}/reveal`

Toggle identity reveal for a candidate (per job context).

**Request Body:**
```json
{
  "job_id": "uuid",
  "revealed": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "candidate_id": "uuid",
    "job_id": "uuid",
    "identity_revealed": true,
    "real_name": "John Doe",
    "real_email": "john@example.com"
  }
}
```

---

### 5.4 `GET /api/v1/candidates/{candidate_id}`

Get candidate's cross-job profile (all jobs they've been evaluated against).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-03-20T14:30:00Z",
    "jobs_evaluated": [
      {
        "job_id": "uuid",
        "job_title": "Senior Full-Stack Engineer",
        "overall_score": 89.0,
        "status": "completed",
        "processed_at": "2026-03-20T14:30:45Z"
      }
    ]
  }
}
```

---

## 6. Feedback APIs

**Owner:** Person 1 (routes) + Person 2 (FeedbackAgent)

### 6.1 `POST /api/v1/candidates/{candidate_id}/feedback`

Generate AI feedback for a candidate-job pair. **Side effect:** Triggers `FeedbackAgent` (Gemini) to produce 150–200 word constructive feedback.

**Request Body:**
```json
{
  "job_id": "uuid"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "candidate_id": "uuid",
    "job_id": "uuid",
    "content": "Thank you for applying for the Senior Full-Stack Engineer position. After careful review, we wanted to provide constructive feedback on your application.\n\nYour Python expertise (8 years) and full-stack experience with React and PostgreSQL strongly align with our core requirements. Your Master's in Computer Science also exceeds our educational expectations.\n\nTo strengthen future applications for similar roles, we recommend:\n\n1. Gaining hands-on Kubernetes experience — your Docker background provides an excellent foundation for container orchestration.\n2. Extending your Docker experience to meet senior-level expectations (3+ years).\n\nYour overall profile shows strong potential for full-stack engineering roles. We encourage you to apply for future openings as you continue developing your cloud infrastructure skills.",
    "generated_at": "2026-03-20T15:00:00Z",
    "sent": false
  }
}
```

---

### 6.2 `GET /api/v1/candidates/{candidate_id}/feedback?job_id={job_id}`

Retrieve previously generated feedback.

**Response (200 OK):** Same as above. Returns 404 if no feedback has been generated yet.

---

### 6.3 `PATCH /api/v1/feedback/{feedback_id}/send`

Mark feedback as sent.

**Request Body:**
```json
{
  "sent": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "sent": true,
    "sent_at": "2026-03-20T15:05:00Z"
  }
}
```

---

## 7. Dashboard APIs

**Owner:** Person 1 (Backend Core)

### 7.1 `GET /api/v1/dashboard/stats`

Aggregated statistics for the current user's dashboard.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "active_jobs": 3,
    "total_jobs": 7,
    "total_resumes_processed": 156,
    "resumes_processing": 2,
    "avg_score": 68.4,
    "avg_processing_time_seconds": 32,
    "top_candidates": [
      {
        "candidate_id": "uuid",
        "anonymized_name": "[CANDIDATE_42]",
        "job_title": "Senior Full-Stack Engineer",
        "overall_score": 94.2
      },
      {
        "candidate_id": "uuid",
        "anonymized_name": "[CANDIDATE_17]",
        "job_title": "Data Engineer",
        "overall_score": 91.8
      }
    ],
    "recent_activity": [
      {
        "type": "resume_processed",
        "job_title": "Senior Full-Stack Engineer",
        "candidate_name": "[CANDIDATE_42]",
        "score": 94.2,
        "timestamp": "2026-03-20T14:30:45Z"
      },
      {
        "type": "job_created",
        "job_title": "Data Engineer",
        "timestamp": "2026-03-20T12:00:00Z"
      },
      {
        "type": "feedback_generated",
        "job_title": "Frontend Developer",
        "candidate_name": "[CANDIDATE_11]",
        "timestamp": "2026-03-20T11:45:00Z"
      }
    ],
    "score_distribution": {
      "90_100": 5,
      "80_89": 12,
      "70_79": 28,
      "60_69": 35,
      "50_59": 40,
      "below_50": 36
    }
  }
}
```

---

## 8. WebSocket Contract

**Owner:** Person 2 (AI Pipeline)

### 8.1 Connection

```
WS {BACKEND_URL}/ws/pipeline/{job_id}?token={jwt_token}
```

**Auth:** JWT passed as query param (WebSocket doesn't support custom headers easily).

**Connection lifecycle:**
1. Frontend opens WebSocket when user navigates to resume upload page for a job
2. Server authenticates via token, verifies user owns the job
3. Server sends events for all resumes being processed under that job
4. Frontend closes connection when navigating away

---

### 8.2 Server → Client Events

**Event envelope:**
```json
{
  "event": "pipeline_update",
  "data": { ... }
}
```

**Pipeline stage update:**
```json
{
  "event": "pipeline_update",
  "data": {
    "resume_id": "uuid",
    "candidate_id": "uuid",
    "filename": "john_doe_resume.pdf",
    "stage": "graph_ingestion",
    "status": "in_progress",
    "progress": 50,
    "message": "Ingesting skills into knowledge graph..."
  }
}
```

| Field | Type | Values |
|---|---|---|
| `stage` | string | `queued`, `parsing`, `filtering`, `graph_ingestion`, `embedding`, `hybrid_matching`, `scoring`, `completed`, `failed` |
| `status` | string | `in_progress`, `completed`, `failed` |
| `progress` | int | 0–100 (percentage within current stage) |
| `message` | string | Human-readable status message |

**Pipeline completed event (includes scores):**
```json
{
  "event": "pipeline_completed",
  "data": {
    "resume_id": "uuid",
    "candidate_id": "uuid",
    "filename": "john_doe_resume.pdf",
    "overall_score": 89.0,
    "skills_score": 94.4,
    "semantic_score": 86.0,
    "experience_score": 73.4,
    "education_score": 100.0,
    "processing_time_seconds": 32
  }
}
```

**Pipeline failed event:**
```json
{
  "event": "pipeline_failed",
  "data": {
    "resume_id": "uuid",
    "filename": "corrupt_file.pdf",
    "stage": "parsing",
    "error": "Unable to extract text from PDF — file may be image-based or corrupted"
  }
}
```

**Heartbeat (every 30s):**
```json
{
  "event": "heartbeat",
  "data": { "timestamp": "2026-03-20T14:30:00Z" }
}
```

---

### 8.3 Client → Server Events

**Ping (keep-alive):**
```json
{
  "event": "ping"
}
```

**Server responds:**
```json
{
  "event": "pong",
  "data": { "timestamp": "2026-03-20T14:30:00Z" }
}
```

---

### 8.4 Stage Sequence Per Resume

```
queued → parsing → filtering → graph_ingestion (parallel with embedding)
                              → embedding       (parallel with graph_ingestion)
                              → hybrid_matching → scoring → completed
```

The frontend should render `graph_ingestion` and `embedding` as parallel steps. Both must complete before `hybrid_matching` begins.

---

## 9. Database Schema (Supabase PostgreSQL)

**Owner:** Person 1 (Backend Core) — Alembic migrations

### 9.1 `users` table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('recruiter', 'hiring_manager')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

---

### 9.2 `jobs` table

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    requirements JSONB NOT NULL DEFAULT '[]',
    education JSONB,
    experience_years INTEGER,
    location VARCHAR(200),
    salary_range JSONB,
    scoring_weights JSONB NOT NULL DEFAULT '{"structural": 0.50, "semantic": 0.30, "experience": 0.15, "education": 0.05}',
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'draft')),
    embedding_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'completed', 'failed')),
    embedding_id VARCHAR(255),
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_created_by ON jobs(created_by);
CREATE INDEX idx_jobs_status ON jobs(status);
```

**`requirements` JSONB shape:**
```json
[
  { "skill": "Python", "priority": "must-have", "min_years": 4 },
  { "skill": "Docker", "priority": "nice-to-have", "min_years": 1 }
]
```

**`scoring_weights` JSONB shape:**
```json
{
  "structural": 0.50,
  "semantic": 0.30,
  "experience": 0.15,
  "education": 0.05
}
```

---

### 9.3 `candidates` table

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_candidates_email ON candidates(email);
```

**Notes:**
- De-duplicated by email. If a resume is uploaded and the parsed email matches an existing candidate, link to existing record.
- `name` is populated from resume parsing but anonymized in scoring views.

---

### 9.4 `resumes` table

```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size INTEGER,
    raw_text TEXT,
    parsed_json JSONB,
    anonymized_text TEXT,
    embedding_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    pipeline_stage VARCHAR(30) DEFAULT 'queued',
    error_message TEXT,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,

    UNIQUE(candidate_id, job_id)
);

CREATE INDEX idx_resumes_job_id ON resumes(job_id);
CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_resumes_status ON resumes(status);
```

**`parsed_json` JSONB shape:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "skills": [
    { "name": "Python", "years": 8, "proficiency": "expert" }
  ],
  "experience": [
    {
      "company": "TechCorp",
      "role": "Senior Engineer",
      "start": "2020-01",
      "end": "present",
      "duration_years": 6,
      "description": "Led development..."
    }
  ],
  "education": [
    {
      "degree": "Master of Science",
      "field": "Computer Science",
      "institution": "MIT",
      "year": 2018
    }
  ]
}
```

---

### 9.5 `analyses` table

```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    overall_score FLOAT NOT NULL,
    skills_score FLOAT NOT NULL,
    semantic_score FLOAT NOT NULL,
    experience_score FLOAT NOT NULL,
    education_score FLOAT NOT NULL,
    skill_matches JSONB NOT NULL DEFAULT '[]',
    strengths JSONB NOT NULL DEFAULT '[]',
    gaps JSONB NOT NULL DEFAULT '[]',
    explanation TEXT NOT NULL,
    education_detail JSONB,
    experience_summary JSONB,
    identity_revealed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(resume_id)
);

CREATE INDEX idx_analyses_job_id ON analyses(job_id);
CREATE INDEX idx_analyses_candidate_id ON analyses(candidate_id);
CREATE INDEX idx_analyses_overall_score ON analyses(overall_score DESC);
```

**`skill_matches` JSONB shape:**
```json
[
  {
    "required_skill": "Python",
    "candidate_skill": "Python",
    "match_type": "direct",
    "credit": 1.0,
    "candidate_years": 8,
    "required_years": 5,
    "priority": "must-have"
  },
  {
    "required_skill": "Kubernetes",
    "candidate_skill": "Docker",
    "match_type": "similar",
    "similarity_score": 0.72,
    "credit": 0.72,
    "candidate_years": 2,
    "required_years": 2,
    "priority": "nice-to-have"
  }
]
```

---

### 9.6 `feedback` table

```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sent BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(candidate_id, job_id)
);

CREATE INDEX idx_feedback_candidate_job ON feedback(candidate_id, job_id);
```

---

### 9.7 Entity Relationship Diagram

```
┌──────────┐       1:N       ┌──────────┐      N:1       ┌────────────┐
│  users   │───────────────►│   jobs    │◄──────────────│ candidates │
│          │  created_by     │          │   (via         │            │
└──────────┘                 └──────────┘   resumes)     └────────────┘
                                  │                           │
                              1:N │                       1:N │
                                  ▼                           ▼
                             ┌──────────┐              ┌──────────┐
                             │ resumes  │──────────────│ analyses │
                             │          │    1:1       │          │
                             └──────────┘              └──────────┘
                                  │
                              N:1 │ (candidate + job)
                                  ▼
                             ┌──────────┐
                             │ feedback │
                             └──────────┘
```

**Cascade rules:**
- Delete user → deletes all their jobs → deletes resumes → deletes analyses + feedback
- Delete job → deletes resumes → deletes analyses + feedback
- Delete candidate → deletes resumes → deletes analyses + feedback

---

## 10. Knowledge Graph Schema (Neo4j)

**Owner:** Person 2 (AI Pipeline)

### 10.1 Node Types

| Node Label | Properties | Created When |
|---|---|---|
| `Candidate` | `id` (UUID, matches PG), `anonymized_name` | Resume pipeline — `GraphIngestionAgent` |
| `Job` | `id` (UUID, matches PG), `title` | Job creation — `GraphIngestionAgent` for JD |
| `Skill` | `name` (normalized lowercase), `category` | Resume/JD ingestion — `GraphIngestionAgent` |
| `SkillCluster` | `name` (e.g., "Programming Languages") | Resume/JD ingestion — `GraphIngestionAgent` |
| `Company` | `name` | Resume ingestion — `GraphIngestionAgent` |
| `Role` | `title` | Resume ingestion — `GraphIngestionAgent` |
| `Education` | `level` (int: 1–5), `field` | Resume/JD ingestion — `GraphIngestionAgent` |
| `Institution` | `name` (always `[UNIVERSITY]` after bias filter) | Resume ingestion — `GraphIngestionAgent` |

### 10.2 Relationships

| Relationship | From → To | Properties | Created When |
|---|---|---|---|
| `HAS_SKILL` | Candidate → Skill | `years`, `proficiency` | Resume ingestion |
| `REQUIRES_SKILL` | Job → Skill | `priority`, `min_years` | JD ingestion |
| `IS_SIMILAR_TO` | Skill ↔ Skill | `score` (0.0–1.0) | Auto-created when Qdrant finds cosine similarity > 0.7 between two skill vectors without existing edge |
| `BELONGS_TO` | Skill → SkillCluster | — | Resume/JD ingestion (Gemini classification) |
| `WORKED_AT` | Candidate → Company | `duration_years`, `start`, `end` | Resume ingestion |
| `HELD_ROLE` | Candidate → Role | `title` | Resume ingestion |
| `HAS_DEGREE` | Candidate → Education | `level`, `field` | Resume ingestion |
| `REQUIRES_DEGREE` | Job → Education | `min_level` | JD ingestion |
| `STUDIED_AT` | Candidate → Institution | — | Resume ingestion (**excluded from scoring**) |

### 10.3 Idempotency

All graph ingestion uses `MERGE` (not `CREATE`) to prevent duplicates:
- Skills normalized to lowercase before merging
- Candidate nodes merge on `id` (UUID from Supabase)
- Job nodes merge on `id` (UUID from Supabase)

### 10.4 Self-Enriching Mechanism

After every resume is embedded:
1. `EmbeddingAgent` queries Qdrant for skills with cosine similarity > 0.7
2. If no `IS_SIMILAR_TO` edge exists in Neo4j between those skills → auto-create it
3. Future candidates benefit from richer partial credit paths

---

## 11. Vector Store Schema (Qdrant)

**Owner:** Person 2 (AI Pipeline)

### 11.1 Collections

| Collection | Vector Dim | Distance | Purpose |
|---|---|---|---|
| `resumes` | 768 | Cosine | Resume text embeddings |
| `job_descriptions` | 768 | Cosine | JD text embeddings |

### 11.2 Point Schema — `resumes` collection

```json
{
  "id": "uuid (matches resume_id in PG)",
  "vector": [0.012, -0.034, ...],
  "payload": {
    "candidate_id": "uuid",
    "job_id": "uuid",
    "skills": ["python", "react", "postgresql"]
  }
}
```

### 11.3 Point Schema — `job_descriptions` collection

```json
{
  "id": "uuid (matches job_id in PG)",
  "vector": [0.008, -0.022, ...],
  "payload": {
    "title": "Senior Full-Stack Engineer",
    "required_skills": ["python", "react", "postgresql", "docker", "kubernetes"]
  }
}
```

### 11.4 Queries Used

| Query | When | Agent |
|---|---|---|
| Upsert resume vector | After `EmbeddingAgent` embeds resume | `EmbeddingAgent` |
| Upsert JD vector | After job creation | `EmbeddingAgent` |
| Cosine similarity (resume vs JD) | During scoring | `HybridMatchingAgent` |
| Skill similarity search | After embedding, for self-enriching graph | `EmbeddingAgent` |

---

## 12. Error Handling Contract

### 12.1 Standard Error Codes

| HTTP Status | Error Code | When |
|---|---|---|
| 400 | `BAD_REQUEST` | Malformed request body |
| 401 | `UNAUTHORIZED` | Missing/expired/invalid JWT |
| 403 | `FORBIDDEN` | Valid JWT but insufficient role/ownership |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 409 | `CONFLICT` | Duplicate resource (e.g., email already registered) |
| 413 | `PAYLOAD_TOO_LARGE` | File too large |
| 422 | `VALIDATION_ERROR` | Schema validation failure |
| 429 | `RATE_LIMITED` | Too many requests (Gemini rate limit) |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Neo4j/Qdrant/Gemini unreachable |

### 12.2 Pipeline-Specific Errors

| Error Scenario | Handling |
|---|---|
| PDF text extraction fails | Mark resume as `failed`, stage `parsing`, emit WS `pipeline_failed` event |
| Gemini API rate limited | Retry with exponential backoff (3 attempts, 2s/4s/8s delays) |
| Neo4j connection lost | Retry once; if failed, mark resume `failed`, stage `graph_ingestion` |
| Qdrant connection lost | Retry once; if failed, mark resume `failed`, stage `embedding` |
| Malformed Gemini response | Validate JSON schema; fallback to raw-text scoring without structured parse |

---

## 13. Environment Variables

| Variable | Service | Owner |
|---|---|---|
| `DATABASE_URL` | Supabase PostgreSQL | Person 1 |
| `SUPABASE_URL` | Supabase project URL | Person 1 |
| `SUPABASE_ANON_KEY` | Supabase anon key | Person 1 |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (for storage) | Person 1 |
| `SECRET_KEY` | JWT signing secret | Person 1 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry (default 1440 = 24h) | Person 1 |
| `CORS_ORIGINS` | Allowed frontend origins | Person 1 |
| `GOOGLE_API_KEY` | Gemini API key | Person 2 |
| `NEO4J_URI` | Neo4j connection URI | Person 2 |
| `NEO4J_USERNAME` | Neo4j username | Person 2 |
| `NEO4J_PASSWORD` | Neo4j password | Person 2 |
| `QDRANT_URL` | Qdrant instance URL | Person 2 |
| `QDRANT_API_KEY` | Qdrant Cloud API key | Person 2 |

---

## 14. Integration Sequence Diagrams

### 14.1 Resume Upload → Full Pipeline

```
Frontend                    Backend (FastAPI)             AI Pipeline                  Neo4j      Qdrant     Supabase
   │                              │                           │                         │          │          │
   │── POST /jobs/{id}/resumes ──►│                           │                         │          │          │
   │   (multipart files)          │── Store files ───────────────────────────────────────────────────────────►│
   │                              │◄─ file_path ────────────────────────────────────────────────────────────│
   │                              │── Create resume rows ──────────────────────────────────────────────────►│
   │                              │── Trigger PipelineOrchestrator (BackgroundTask) ──►│                    │
   │◄─ 202 Accepted ─────────────│                           │                         │          │          │
   │                              │                           │                         │          │          │
   │── WS /ws/pipeline/{job_id} ─►│                           │                         │          │          │
   │◄─ connected ────────────────│                           │                         │          │          │
   │                              │                           │                         │          │          │
   │                              │   ┌─ For each resume ────┐                         │          │          │
   │                              │   │                       │                         │          │          │
   │◄─ WS: stage=parsing ────────│◄──│── ResumeParserAgent ──│── Gemini parse ────────►│          │          │
   │                              │   │   (extract + LLM)     │◄─ structured JSON ─────│          │          │
   │                              │   │                       │                         │          │          │
   │◄─ WS: stage=filtering ──────│◄──│── BiasFilterAgent ────│  (in-memory)            │          │          │
   │                              │   │                       │                         │          │          │
   │                              │   │   ┌─ PARALLEL ───────┐│                         │          │          │
   │◄─ WS: stage=graph_ingestion─│◄──│───│─GraphIngestion────│├── MERGE nodes/rels ───►│          │          │
   │◄─ WS: stage=embedding ──────│◄──│───│─EmbeddingAgent────│├── Gemini embed ────────►│──upsert─►│          │
   │                              │   │   └──────────────────┘│                         │          │          │
   │                              │   │                       │                         │          │          │
   │◄─ WS: stage=hybrid_matching─│◄──│── HybridMatchingAgent─│── Cypher queries ──────►│          │          │
   │                              │   │                       │── Cosine search ────────────────────►│          │
   │                              │   │                       │◄─ fused scores ─────────│◄─────────│          │
   │                              │   │                       │                         │          │          │
   │◄─ WS: stage=scoring ────────│◄──│── ScoringAgent ───────│── Gemini prompt ────────►│          │          │
   │                              │   │                       │◄─ explanation ──────────│          │          │
   │                              │   │                       │── Save analysis ────────────────────────────►│
   │                              │   │                       │                         │          │          │
   │◄─ WS: pipeline_completed ───│◄──│── Update resume row ──│                         │          │          │
   │   (includes scores)         │   │                       │                         │          │          │
   │                              │   └───────────────────────┘                         │          │          │
```

### 14.2 Job Creation → JD Processing

```
Frontend                    Backend                       AI Pipeline              Neo4j      Qdrant
   │                              │                           │                      │          │
   │── POST /api/v1/jobs ────────►│                           │                      │          │
   │                              │── Insert job row (PG) ───►│                      │          │
   │                              │── BackgroundTask ─────────►│                      │          │
   │◄─ 201 Created ──────────────│                           │                      │          │
   │   (embedding_status:         │                           │                      │          │
   │    processing)               │                           │                      │          │
   │                              │                           │── EmbeddingAgent ─────────────►│
   │                              │                           │   (JD → 768-dim vector)        │
   │                              │                           │                      │          │
   │                              │                           │── GraphIngestionAgent ──────►│  │
   │                              │                           │   (REQUIRES_SKILL,    │          │
   │                              │                           │    REQUIRES_DEGREE)   │          │
   │                              │                           │                      │          │
   │                              │◄─ Update embedding_status=completed ─────────────│          │
```

### 14.3 Feedback Generation

```
Frontend                    Backend                       AI Pipeline (FeedbackAgent)
   │                              │                           │
   │── POST /candidates/{id}/     │                           │
   │   feedback {job_id} ────────►│                           │
   │                              │── Load analysis from PG ──►│
   │                              │── Load skill_matches ─────►│
   │                              │── FeedbackAgent ──────────►│── Gemini prompt ──────►
   │                              │                           │◄─ 150-200 word feedback──
   │                              │── Save to feedback table ──►│
   │◄─ 201 Created ──────────────│                           │
   │   (feedback content)         │                           │
```

---

## Appendix A: API Endpoint Summary

| Method | Endpoint | Owner | Auth | Purpose |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | P1 | No | Create account |
| `POST` | `/api/v1/auth/login` | P1 | No | Get JWT token |
| `GET` | `/api/v1/auth/me` | P1 | Yes | Current user profile |
| `PUT` | `/api/v1/auth/me` | P1 | Yes | Update profile |
| `POST` | `/api/v1/jobs` | P1+P2 | Yes | Create job (triggers JD pipeline) |
| `GET` | `/api/v1/jobs` | P1 | Yes | List user's jobs |
| `GET` | `/api/v1/jobs/{job_id}` | P1 | Yes | Get job detail |
| `PUT` | `/api/v1/jobs/{job_id}` | P1+P2 | Yes | Update job |
| `PATCH` | `/api/v1/jobs/{job_id}/status` | P1 | Yes | Change job status |
| `DELETE` | `/api/v1/jobs/{job_id}` | P1 | Yes | Delete job + cascades |
| `POST` | `/api/v1/jobs/{job_id}/resumes` | P1+P2 | Yes | Upload resumes (triggers pipeline) |
| `GET` | `/api/v1/jobs/{job_id}/resumes` | P1 | Yes | List resumes for job |
| `GET` | `/api/v1/resumes/{resume_id}` | P1 | Yes | Resume detail |
| `GET` | `/api/v1/resumes/{resume_id}/download` | P1 | Yes | Download original file |
| `GET` | `/api/v1/jobs/{job_id}/candidates` | P1 | Yes | Ranked candidate list |
| `GET` | `/api/v1/candidates/{candidate_id}/analysis` | P1 | Yes | Full analysis detail |
| `PATCH` | `/api/v1/candidates/{candidate_id}/reveal` | P1 | Yes | Toggle identity reveal |
| `GET` | `/api/v1/candidates/{candidate_id}` | P1 | Yes | Cross-job candidate profile |
| `POST` | `/api/v1/candidates/{candidate_id}/feedback` | P1+P2 | Yes | Generate AI feedback |
| `GET` | `/api/v1/candidates/{candidate_id}/feedback` | P1 | Yes | Get existing feedback |
| `PATCH` | `/api/v1/feedback/{feedback_id}/send` | P1 | Yes | Mark feedback as sent |
| `GET` | `/api/v1/dashboard/stats` | P1 | Yes | Dashboard aggregated stats |
| `WS` | `/ws/pipeline/{job_id}` | P2 | Token | Real-time pipeline updates |

**Total: 21 REST endpoints + 1 WebSocket channel**

---

## Appendix B: Frontend → API Mapping

| Frontend Page | APIs Consumed |
|---|---|
| **Landing Page** | None (static) |
| **Login** | `POST /auth/login` |
| **Register** | `POST /auth/register` |
| **Dashboard** | `GET /dashboard/stats` |
| **Job List** | `GET /jobs` |
| **Create Job** | `POST /jobs` |
| **Job Detail** | `GET /jobs/{id}`, `PATCH /jobs/{id}/status`, `DELETE /jobs/{id}` |
| **Resume Upload** | `POST /jobs/{id}/resumes`, `GET /jobs/{id}/resumes`, `WS /ws/pipeline/{job_id}` |
| **Candidate List** | `GET /jobs/{id}/candidates` |
| **Candidate Detail** | `GET /candidates/{id}/analysis?job_id=`, `PATCH /candidates/{id}/reveal` |
| **Feedback** | `POST /candidates/{id}/feedback`, `GET /candidates/{id}/feedback`, `PATCH /feedback/{id}/send` |
| **Settings** | `GET /auth/me`, `PUT /auth/me` |

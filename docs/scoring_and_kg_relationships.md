# RAX — Scoring Criteria & Knowledge Graph Relationships

---

## 1. How Scoring Works

RAX uses **multi-dimensional scoring** instead of a single similarity number. Every candidate is evaluated across four components that are fused into a final hybrid score.

### 1.1 The Scoring Formula

```
Final Score = 0.50 × Structural Skill Match  (Knowledge Graph — Neo4j)
            + 0.30 × Semantic Similarity      (Vector Search — Qdrant)
            + 0.15 × Experience Match          (Knowledge Graph — Neo4j)
            + 0.05 × Education Match           (Knowledge Graph — Neo4j)
```

> Weights are **configurable per job**. If one signal is weak (e.g., sparse graph for a poorly parsed resume), the other signals naturally compensate.

---

### 1.2 Breaking Down Each Scoring Dimension

#### A. Structural Skill Match — 50% weight (Neo4j Knowledge Graph)

This is the **heaviest component** and the core differentiator.

**What it measures:** How many of the job's required skills does the candidate actually possess, verified through explicit graph relationships.

**How it's computed:**

1. The `HybridMatchingAgent` runs a Cypher query against Neo4j:
   ```cypher
   MATCH (j:Job {id: $job_id})-[:REQUIRES_SKILL]->(s:Skill)<-[:HAS_SKILL]-(c:Candidate {id: $candidate_id})
   RETURN s.name AS matched_skill, j_rel.priority AS priority, j_rel.min_years AS required_years, c_rel.years AS candidate_years
   ```

2. It also checks for **adjacent/similar skills** via `IS_SIMILAR_TO` edges:
   ```cypher
   MATCH (j:Job {id: $job_id})-[:REQUIRES_SKILL]->(required:Skill)
   WHERE NOT (c)-[:HAS_SKILL]->(required)
   MATCH (c:Candidate {id: $candidate_id})-[:HAS_SKILL]->(has:Skill)-[:IS_SIMILAR_TO {score: sim}]->(required)
   WHERE sim > 0.7
   RETURN required.name AS gap_skill, has.name AS similar_skill, sim AS similarity
   ```

3. **Scoring logic:**
   - Direct match on a required skill → full credit (1.0)
   - Match via `IS_SIMILAR_TO` edge → partial credit (similarity score, e.g., 0.87)
   - No match at all → 0.0
   - Priority-weighted: `must-have` skills carry more weight than `nice-to-have`

**Example output:**
| Required Skill | Candidate Has | Match Type | Credit |
|---|---|---|---|
| Python | Python (8 yrs) | Direct | 1.00 |
| SQL | SQL (5 yrs) | Direct | 1.00 |
| AWS | AWS (3 yrs) | Direct | 1.00 |
| Docker | Docker (2 yrs) | Direct | 1.00 |
| Kubernetes | — | Via IS_SIMILAR_TO (Docker → K8s, 0.72) | 0.72 |

**Structural Score = (1.0 + 1.0 + 1.0 + 1.0 + 0.72) / 5 = 0.944**

---

#### B. Semantic Similarity — 30% weight (Qdrant Vector Search)

**What it measures:** How semantically similar is the candidate's overall resume to the job description — capturing context, tone, and vocabulary that structured matching might miss.

**How it's computed:**

1. Both the resume and JD are embedded into **768-dimensional vectors** using Gemini `text-embedding-004`
2. The `HybridMatchingAgent` queries Qdrant for cosine similarity:
   ```
   cosine_similarity(resume_vector, job_description_vector)
   ```
3. The result is a score between 0.0 and 1.0

**Why it matters:**
- Catches meaning even when exact skill names differ ("ML Engineer" vs "Machine Learning Specialist")
- Provides a safety net when the knowledge graph is sparse (poorly parsed resume)
- Captures overall career direction and domain alignment

**Example:** A resume mentioning "built scalable microservices on GCP" gets high semantic similarity to a JD asking for "cloud-native distributed systems engineer" — even if the exact terms don't appear in the graph.

---

#### C. Experience Match — 15% weight (Neo4j Knowledge Graph)

**What it measures:** Does the candidate's years of experience per skill meet, exceed, or fall short of the job's requirements?

**How it's computed:**

1. Cypher query compares `HAS_SKILL.years` against `REQUIRES_SKILL.min_years`:
   ```cypher
   MATCH (j:Job {id: $job_id})-[req:REQUIRES_SKILL]->(s:Skill)<-[has:HAS_SKILL]-(c:Candidate {id: $candidate_id})
   RETURN s.name, has.years AS candidate_years, req.min_years AS required_years,
          CASE WHEN has.years >= req.min_years THEN 1.0
               ELSE toFloat(has.years) / req.min_years
          END AS experience_score
   ```

2. Per-skill experience scores are averaged across all required skills

**Example output:**
| Skill | Candidate Years | Required Years | Score |
|---|---|---|---|
| Python | 8 | 5 | 1.00 (surplus) |
| SQL | 5 | 3 | 1.00 (surplus) |
| AWS | 3 | 3 | 1.00 (meets) |
| Docker | 2 | 3 | 0.67 (gap) |
| Kubernetes | 0 | 2 | 0.00 (missing) |

**Experience Score = (1.0 + 1.0 + 1.0 + 0.67 + 0.0) / 5 = 0.734**

---

#### D. Education Match — 5% weight (Neo4j Knowledge Graph)

**What it measures:** Does the candidate's degree level meet or exceed the job's education requirements?

**How it's computed:**

1. Degree levels are mapped to a numeric scale:
   ```
   High School = 1, Associate = 2, Bachelor = 3, Master = 4, PhD = 5
   ```

2. Cypher query:
   ```cypher
   MATCH (c:Candidate {id: $candidate_id})-[:HAS_DEGREE]->(e:Education)
   MATCH (j:Job {id: $job_id})-[req:REQUIRES_DEGREE]->(reqEdu:Education)
   RETURN e.level AS candidate_level, reqEdu.min_level AS required_level,
          CASE WHEN e.level >= reqEdu.min_level THEN 1.0
               ELSE toFloat(e.level) / reqEdu.min_level
          END AS education_score
   ```

**Example:** Candidate has Master's (4), Job requires Bachelor's (3) → Score = 1.0

---

### 1.3 Final Score Computation — Worked Example

| Dimension | Raw Score | Weight | Weighted |
|---|---|---|---|
| Structural Skill Match | 0.944 | × 0.50 | 0.472 |
| Semantic Similarity | 0.860 | × 0.30 | 0.258 |
| Experience Match | 0.734 | × 0.15 | 0.110 |
| Education Match | 1.000 | × 0.05 | 0.050 |
| **Final Hybrid Score** | | | **0.890 (89/100)** |

This score is then passed to the `ScoringAgent`, which sends the hybrid context (graph paths, similarity score, experience comparisons) to **Gemini (gemini-1.5-pro)** to generate:

- **Multi-dimensional sub-scores:** skills_score, experience_score, education_score (for the radar chart)
- **Strengths list:** "Deep Python expertise (8 years), strong cloud background (AWS), full-stack database skills (SQL)"
- **Gaps list:** "No Kubernetes experience (required 2 years), Docker experience below threshold"
- **Natural language explanation:** "Strong technical match with deep Python and cloud experience. Primary gap is container orchestration (Kubernetes). Recommend for interview with focus on infrastructure skills."

---

### 1.4 What Makes This Different from Competitors

| Aspect | Competitors (e.g., Greenhouse, Ideal) | RAX |
|---|---|---|
| Scoring method | Single opaque score or keyword count | 4-dimension weighted hybrid score |
| Explainability | "Score: 85" — no reason given | Named graph paths, per-skill match/gap, AI narrative |
| Partial credit | Binary match/no-match | Similar skills get proportional credit via IS_SIMILAR_TO |
| Experience depth | Ignored or manual | Automated year-by-year comparison from graph properties |
| Configurability | Fixed algorithm | Weights tunable per job posting |
| Self-improvement | Static model | Graph auto-enriches with new IS_SIMILAR_TO edges over time |

---

## 2. Knowledge Graph Relationships We Check

The Neo4j knowledge graph is the structural backbone of RAX. Below are **all node types and relationships** that are created, queried, and checked during the scoring pipeline.

### 2.1 Node Types

| Node Label | Description | Key Properties | Created By |
|---|---|---|---|
| `Candidate` | A job applicant | `id`, `anonymized_name` | GraphIngestionAgent |
| `Job` | A job posting | `id`, `title` | When recruiter creates a job |
| `Skill` | A technical or soft skill | `name`, `category` | GraphIngestionAgent (from resume + JD) |
| `SkillCluster` | A skill category grouping | `name` (e.g., "Programming Languages") | GraphIngestionAgent |
| `Company` | A company the candidate worked at | `name`, `industry` | GraphIngestionAgent |
| `Role` | A job title/role held | `title` | GraphIngestionAgent |
| `Education` | A degree type | `level` (Bachelor, Master, PhD), `field` | GraphIngestionAgent |
| `Institution` | A university/school | `name` | GraphIngestionAgent (anonymized to `[UNIVERSITY]` for scoring) |

---

### 2.2 All Relationships & What They Mean

#### Candidate → Skill: `HAS_SKILL`
```cypher
(Candidate)-[:HAS_SKILL {years: 8, proficiency: "expert"}]->(Skill {name: "Python"})
```
- **Properties:** `years` (integer), `proficiency` (beginner/intermediate/expert)
- **Used in scoring:** Structural Skill Match (50%) + Experience Match (15%)
- **What we check:** Does the candidate possess the skill? For how many years? At what proficiency?

#### Job → Skill: `REQUIRES_SKILL`
```cypher
(Job)-[:REQUIRES_SKILL {priority: "must-have", min_years: 5}]->(Skill {name: "Python"})
```
- **Properties:** `priority` (must-have/nice-to-have), `min_years` (integer)
- **Used in scoring:** Compared against `HAS_SKILL` to compute match and experience gap
- **What we check:** Which skills does the job require? What are the minimum years? Is it mandatory or optional?

#### Skill → Skill: `IS_SIMILAR_TO`
```cypher
(Skill {name: "Django"})-[:IS_SIMILAR_TO {score: 0.89}]->(Skill {name: "Flask"})
```
- **Properties:** `score` (0.0–1.0, from Qdrant embedding proximity)
- **Used in scoring:** Partial credit when a candidate doesn't have the exact required skill but has a similar one
- **What we check:** If candidate lacks Skill X but has Skill Y that is similar (score > 0.7), award proportional credit
- **Self-enriching:** New `IS_SIMILAR_TO` edges are **auto-discovered** — when Qdrant finds two skill embeddings are close, the system creates this edge in Neo4j

#### Skill → SkillCluster: `BELONGS_TO`
```cypher
(Skill {name: "Python"})-[:BELONGS_TO]->(SkillCluster {name: "Programming Languages"})
(SkillCluster {name: "Programming Languages"})-[:BELONGS_TO]->(SkillCluster {name: "Technical Skills"})
```
- **Used in scoring:** Enables hierarchical skill reasoning — if a job requires "Programming Languages" broadly, any language in that cluster counts
- **What we check:** Skill taxonomy hierarchy for group-level matching

#### Candidate → Company: `WORKED_AT`
```cypher
(Candidate)-[:WORKED_AT {duration: "3 years", start: "2021", end: "2024"}]->(Company {name: "Acme Corp"})
```
- **Properties:** `duration`, `start`, `end`
- **Used in scoring:** Experience depth validation, multi-hop reasoning
- **What we check:** Career progression, industry relevance, tenure stability

#### Candidate → Role: `HELD_ROLE`
```cypher
(Candidate)-[:HELD_ROLE {title: "Senior Backend Engineer"}]->(Role)
```
- **Used in scoring:** Role-level matching (e.g., job requires "Senior" level → candidate held senior titles)
- **What we check:** Seniority alignment, role relevance

#### Candidate → Education: `HAS_DEGREE`
```cypher
(Candidate)-[:HAS_DEGREE {level: "Master", field: "Computer Science"}]->(Education)
```
- **Properties:** `level` (mapped to numeric: Bachelor=3, Master=4, PhD=5), `field`
- **Used in scoring:** Education Match (5%)
- **What we check:** Does the degree level meet or exceed the requirement? Is the field relevant?

#### Job → Education: `REQUIRES_DEGREE`
```cypher
(Job)-[:REQUIRES_DEGREE {min_level: "Bachelor"}]->(Education)
```
- **Properties:** `min_level`
- **Used in scoring:** Compared against `HAS_DEGREE` to compute education fit
- **What we check:** Minimum education threshold

#### Candidate → Institution: `STUDIED_AT`
```cypher
(Candidate)-[:STUDIED_AT]->(Institution {name: "[UNIVERSITY]"})
```
- **Important:** Institution name is **anonymized** by the `BiasFilterAgent` before scoring
- **Used in scoring:** NOT used — intentionally excluded to prevent bias
- **What we check:** Post-scoring, this relationship exists for revealing identity during "Reveal Identity" toggle

---

### 2.3 How Relationships Flow Through the Scoring Pipeline

```
Step 1: STRUCTURAL SKILL MATCH (50%)
─────────────────────────────────────
Query: (Job)-[:REQUIRES_SKILL]->(Skill)<-[:HAS_SKILL]-(Candidate)
  → Count direct matches
  → For gaps: check (Candidate)-[:HAS_SKILL]->(Skill)-[:IS_SIMILAR_TO]->(RequiredSkill)
  → Apply priority weights (must-have > nice-to-have)
  → Result: structural_score (0.0 – 1.0)

Step 2: SEMANTIC SIMILARITY (30%)
─────────────────────────────────
Query: Qdrant cosine_similarity(resume_vector, jd_vector)
  → No graph involved — purely vector-based
  → Result: semantic_score (0.0 – 1.0)

Step 3: EXPERIENCE MATCH (15%)
──────────────────────────────
Query: (Job)-[req:REQUIRES_SKILL]->(Skill)<-[has:HAS_SKILL]-(Candidate)
  → Compare has.years vs req.min_years per skill
  → Surplus → 1.0, Partial → proportional, Missing → 0.0
  → Average across all required skills
  → Result: experience_score (0.0 – 1.0)

Step 4: EDUCATION MATCH (5%)
─────────────────────────────
Query: (Candidate)-[:HAS_DEGREE]->(Education) vs (Job)-[:REQUIRES_DEGREE]->(Education)
  → Compare degree levels numerically
  → Meets/exceeds → 1.0, Below → proportional
  → Result: education_score (0.0 – 1.0)

Step 5: FUSION
──────────────
final_score = 0.50 × structural + 0.30 × semantic + 0.15 × experience + 0.05 × education

Step 6: EXPLAINABLE SCORING (ScoringAgent → Gemini)
────────────────────────────────────────────────────
Input: All graph paths + scores + gaps from Steps 1–5
Output: Natural language explanation + strengths list + gaps list + radar chart data
```

---

### 2.4 Graph Relationships Summary Table

| Relationship | From → To | Properties | Scoring Dimension | Weight Contribution |
|---|---|---|---|---|
| `HAS_SKILL` | Candidate → Skill | years, proficiency | Structural (50%) + Experience (15%) | **65% total** |
| `REQUIRES_SKILL` | Job → Skill | priority, min_years | Structural (50%) + Experience (15%) | **65% total** |
| `IS_SIMILAR_TO` | Skill → Skill | score | Structural (50%) — partial credit | Varies by similarity |
| `BELONGS_TO` | Skill → SkillCluster | — | Structural (50%) — group matching | Indirect |
| `WORKED_AT` | Candidate → Company | duration, start, end | Experience (15%) — career context | Indirect |
| `HELD_ROLE` | Candidate → Role | title | Experience (15%) — seniority check | Indirect |
| `HAS_DEGREE` | Candidate → Education | level, field | Education (5%) | **5% total** |
| `REQUIRES_DEGREE` | Job → Education | min_level | Education (5%) | **5% total** |
| `STUDIED_AT` | Candidate → Institution | — | **Excluded** (bias prevention) | **0%** |

---

### 2.5 Explainability via Graph Paths

Every score in RAX is backed by a **traceable graph path**. The recruiter sees not just a number but the explicit reasoning:

**Example explanations generated from graph traversal:**

| What Recruiter Sees | Underlying Graph Path |
|---|---|
| "Direct match: Python ✅" | `(Candidate)-[:HAS_SKILL {years:8}]->(Python)<-[:REQUIRES_SKILL {priority:"must-have"}]-(Job)` |
| "Partial match: Docker → Kubernetes (72%)" | `(Candidate)-[:HAS_SKILL]->(Docker)-[:IS_SIMILAR_TO {score:0.72}]->(Kubernetes)<-[:REQUIRES_SKILL]-(Job)` |
| "Experience surplus: Python +3 years" | `HAS_SKILL.years(8) - REQUIRES_SKILL.min_years(5) = +3` |
| "Experience gap: Kubernetes -2 years" | `HAS_SKILL.years(0) - REQUIRES_SKILL.min_years(2) = -2` |
| "Education exceeds: Master's > Bachelor's" | `(Candidate)-[:HAS_DEGREE {level:"Master"}]->(Education) vs (Job)-[:REQUIRES_DEGREE {min_level:"Bachelor"}]` |
| "Bias verified: No institution influenced score" | `MATCH path FROM (Candidate) TO (Score) WHERE NONE(n IN nodes(path) WHERE n:Institution)` |

---

### 2.6 Self-Enriching Graph (Auto-Discovery)

The knowledge graph **gets smarter with every resume processed**:

1. When the `EmbeddingAgent` stores a new skill embedding in Qdrant, it checks proximity to existing skill embeddings
2. If two skills have cosine similarity > 0.7 in Qdrant but no `IS_SIMILAR_TO` edge in Neo4j → the system **auto-creates** the edge:
   ```cypher
   MERGE (s1:Skill {name: "FastAPI"})-[:IS_SIMILAR_TO {score: 0.85}]->(s2:Skill {name: "Flask"})
   ```
3. Future candidates benefit from this enriched graph — partial credit paths that didn't exist before now become available
4. The skill taxonomy grows organically, reducing false negatives over time

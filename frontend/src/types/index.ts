// ── API Types matching backend Pydantic schemas ──

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'recruiter' | 'hiring_manager';
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Job {
  id: string;
  title: string;
  description: string;
  requirements_raw: Record<string, unknown> | null;
  status: 'draft' | 'active' | 'closed';
  created_by: string;
  created_at: string;
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
}

export interface JobCreate {
  title: string;
  description: string;
  requirements_raw?: Record<string, unknown>;
}

export interface ResumeUploadResponse {
  id: string;
  candidate_id: string;
  job_id: string;
  file_path: string;
  pipeline_status: PipelineStatus;
  created_at: string;
}

export type PipelineStatus =
  | 'uploaded'
  | 'parsing'
  | 'filtering'
  | 'ingesting'
  | 'embedding'
  | 'matching'
  | 'scoring'
  | 'completed'
  | 'failed';

export interface ResumeStatus {
  id: string;
  pipeline_status: PipelineStatus;
  created_at: string;
}

export type NotificationStatus = 'not_sent' | 'shortlisted' | 'rejected';

export interface CandidateWithScores {
  id: string;
  name: string | null;
  email: string | null;
  resume_id: string;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  pipeline_status: PipelineStatus;
  notification_status: NotificationStatus | null;
  explanation: string;
}

export interface CandidateListResponse {
  candidates: CandidateWithScores[];
  total: number;
}

export interface Analysis {
  id: string;
  resume_id: string;
  job_id: string;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  semantic_similarity: number;
  structural_match: number;
  explanation: string;
  strengths: string[];
  gaps: string[];
  graph_paths: string[];
  created_at: string;
}

export interface Feedback {
  id: string;
  candidate_id: string;
  job_id: string;
  resume_id: string;
  content: string;
  sent_at: string | null;
  created_at: string;
}

export interface WsStageEvent {
  resume_id: string;
  stage: string;
  status: 'in_progress' | 'complete' | 'failed';
  timestamp: string;
}

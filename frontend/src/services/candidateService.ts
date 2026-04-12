import api from './api';
import type { CandidateListResponse, Analysis } from '@/types';

export async function getCandidates(
  jobId: string,
  sortBy = 'overall_score',
  order = 'desc'
): Promise<CandidateListResponse> {
  const { data } = await api.get<CandidateListResponse>(
    `/jobs/${jobId}/candidates`,
    { params: { sort_by: sortBy, order } }
  );
  return data;
}

export async function getAnalysis(resumeId: string): Promise<Analysis> {
  const { data } = await api.get<Analysis>(`/resumes/${resumeId}/analysis`);
  return data;
}

export async function deleteResume(resumeId: string): Promise<void> {
  await api.delete(`/resumes/${resumeId}`);
}

export async function notifyCandidate(
  candidateId: string,
  type: 'shortlisted' | 'rejected',
  customMessage?: string
): Promise<{ status: string; email: string }> {
  const { data } = await api.post(`/candidates/${candidateId}/notify`, {
    type,
    custom_message: customMessage,
  });
  return data;
}

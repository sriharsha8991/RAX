import api from './api';
import type { ResumeUploadResponse, ResumeStatus } from '@/types';

export async function uploadResumes(
  files: File[],
  jobId: string
): Promise<ResumeUploadResponse[]> {
  const results: ResumeUploadResponse[] = [];
  for (const file of files) {
    const form = new FormData();
    form.append('file', file);
    form.append('job_id', jobId);
    const { data } = await api.post<ResumeUploadResponse>('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { job_id: jobId },
    });
    results.push(data);
  }
  return results;
}

export async function getResumeStatus(resumeId: string): Promise<ResumeStatus> {
  const { data } = await api.get<ResumeStatus>(`/resumes/${resumeId}/status`);
  return data;
}

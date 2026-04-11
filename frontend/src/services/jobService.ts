import api from './api';
import type { Job, JobCreate, JobListResponse } from '@/types';

export async function getJobs(): Promise<JobListResponse> {
  const { data } = await api.get<JobListResponse>('/jobs');
  return data;
}

export async function getJob(id: string): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}`);
  return data;
}

export async function createJob(body: JobCreate): Promise<Job> {
  const { data } = await api.post<Job>('/jobs', body);
  return data;
}

export async function deleteJob(id: string): Promise<void> {
  await api.delete(`/jobs/${id}`);
}

import api from './api';
import type { Feedback } from '@/types';

export async function generateFeedback(
  candidateId: string,
  jobId: string
): Promise<Feedback> {
  const { data } = await api.post<Feedback>(`/feedback/${candidateId}/${jobId}`);
  return data;
}

export async function getFeedback(feedbackId: string): Promise<Feedback> {
  const { data } = await api.get<Feedback>(`/feedback/${feedbackId}`);
  return data;
}

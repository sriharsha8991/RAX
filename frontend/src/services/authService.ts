import api from './api';
import type { TokenResponse, User } from '@/types';

export async function login(email: string, password: string): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  const { data } = await api.post<TokenResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}

export async function register(
  email: string,
  password: string,
  full_name: string,
  role: 'recruiter' | 'hiring_manager'
): Promise<User> {
  const { data } = await api.post<User>('/auth/register', {
    email,
    password,
    full_name,
    role,
  });
  return data;
}

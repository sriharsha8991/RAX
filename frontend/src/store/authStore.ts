import { create } from 'zustand';
import type { User } from '@/types';
import { login as loginApi, register as registerApi } from '@/services/authService';

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = token.split('.')[1];
    return JSON.parse(atob(base64));
  } catch {
    return {};
  }
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, role: 'recruiter' | 'hiring_manager') => Promise<void>;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const resp = await loginApi(email, password);
    const payload = decodeJwtPayload(resp.access_token);
    const user: User = {
      id: String(payload.sub ?? ''),
      email,
      full_name: '',
      role: (payload.role as 'recruiter' | 'hiring_manager') ?? 'recruiter',
      created_at: '',
    };
    localStorage.setItem('rax_token', resp.access_token);
    localStorage.setItem('rax_user', JSON.stringify(user));
    set({ token: resp.access_token, user, isAuthenticated: true });
  },

  register: async (email, password, fullName, role) => {
    const resp = await registerApi(email, password, fullName, role);
    // Register now returns token directly — no second login call needed
    const token = (resp as unknown as { access_token: string }).access_token;
    const payload = decodeJwtPayload(token);
    const user: User = {
      id: String(payload.sub ?? resp.id ?? ''),
      email,
      full_name: fullName,
      role,
      created_at: '',
    };
    localStorage.setItem('rax_token', token);
    localStorage.setItem('rax_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('rax_token');
    localStorage.removeItem('rax_user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  hydrate: () => {
    const token = localStorage.getItem('rax_token');
    const userStr = localStorage.getItem('rax_user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({ token, user, isAuthenticated: true });
      } catch {
        set({ token: null, user: null, isAuthenticated: false });
      }
    }
  },
}));

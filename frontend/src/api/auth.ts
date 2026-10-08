// Typed auth API module (REQ-FE-042/043).
//
// One function per Chapter 7 §7.3 auth endpoint, 1:1. All calls go through
// the shared `api` instance so interceptors (bearer attach, 401 cleanup,
// error normalization) apply uniformly (REQ-ARCH-070).

import { api } from './client';

/** Public user representation — exactly the five backend fields. */
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

/** Payload for POST /auth/login. */
export interface LoginPayload {
  email: string;
  password: string;
}

/** Payload for POST /auth/register. */
export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
}

/** Response body for POST /auth/login (and register's echoed session). */
export interface LoginResult {
  access_token: string;
  token_type: string;
  user: User;
}

export const login = async (payload: LoginPayload): Promise<LoginResult> => {
  const response = await api.post<LoginResult>('/api/v1/auth/login', payload);
  return response.data;
};

export const register = async (payload: RegisterPayload): Promise<LoginResult> => {
  const response = await api.post<LoginResult>('/api/v1/auth/register', payload);
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await api.get<User>('/api/v1/auth/me');
  return response.data;
};

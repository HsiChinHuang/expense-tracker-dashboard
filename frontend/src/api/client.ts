/// <reference types="vite/client" />

// Centralized axios instance (REQ-FE-040, REQ-TECH-007, REQ-ARCH-070).
//
// This is the ONLY module in the app that talks to axios directly: every
// other module goes through the typed functions in `src/api/`. The request
// interceptor attaches the bearer token from localStorage; the response
// interceptor clears the token on 401 and redirects to /login, and rejects
// with a normalized `ApiError` ({status, code, message, field?}) so the UI
// layer never has to touch raw axios shapes (REQ-FE-041).

import axios, { AxiosError } from 'axios';

/** Normalized API error shape shared across the app (REQ-FE-041). */
export interface ApiError {
  status: number;
  code: string;
  message: string;
  field?: string;
}

/** LocalStorage key holding the JWT (REQ-ARCH-042 — exactly `token`). */
export const TOKEN_KEY = 'token';

/** Error code used when the request never reached the backend. */
export const NETWORK_ERROR_CODE = 'NETWORK_ERROR';

const BACKEND_UNREACHABLE_MESSAGE = 'Could not reach the server. Please try again.';

/**
 * Type guard: the value already carries the normalized error keys.
 * An `AxiosError` also exposes numeric `status` and string `code`
 * properties, so it must be excluded explicitly (it is normalized below).
 */
const isApiError = (value: unknown): value is ApiError =>
  !axios.isAxiosError(value) &&
  typeof value === 'object' &&
  value !== null &&
  !('isAxiosError' in value) &&
  typeof (value as { status?: unknown }).status === 'number' &&
  typeof (value as { code?: unknown }).code === 'string';

/** Read the stored JWT, tolerating a disabled / throwing localStorage. */
const readToken = (): string | null => {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

/** Turn any thrown value into the normalized shape (never returns unknown). */
export const toApiError = (error: unknown): ApiError => {
  if (isApiError(error)) {
    return error;
  }
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: unknown; code?: unknown; field?: unknown }>;
    if (!axiosError.response) {
      return { status: 0, code: NETWORK_ERROR_CODE, message: BACKEND_UNREACHABLE_MESSAGE };
    }
    const body = axiosError.response.data;
    const detail =
      typeof body?.detail === 'string'
        ? body.detail
        : axiosError.message || 'An unexpected error occurred.';
    const code = typeof body?.code === 'string' ? body.code : 'HTTP_ERROR';
    const field = typeof body?.field === 'string' ? body.field : undefined;
    return {
      status: axiosError.response.status,
      code,
      message: detail,
      ...(field ? { field } : {})
    };
  }
  return {
    status: 0,
    code: 'UNKNOWN',
    message: error instanceof Error ? error.message : 'An unexpected error occurred.'
  };
};

const runtimeBaseURL = (
  (import.meta.env as Record<string, string | undefined>)['VITE_API_BASE_URL'] ?? ''
).trim();

/** Single shared axios instance — the app's only HTTP entry point. */
export const api = axios.create({
  baseURL: runtimeBaseURL,
  timeout: 10_000
});

api.interceptors.request.use((config) => {
  const token = readToken();
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const normalized = toApiError(error);
    if (normalized.status === 401) {
      try {
        window.localStorage.removeItem(TOKEN_KEY);
      } catch {
        // A storage-less environment still redirects; the auth context
        // keeps its in-memory state authoritative.
      }
      window.location.href = '/login';
    }
    return Promise.reject(normalized);
  }
);

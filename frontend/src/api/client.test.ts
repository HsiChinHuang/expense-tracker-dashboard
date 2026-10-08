// AC1: axios client behavior — base URL/timeout, bearer attach, 401
// cleanup + redirect, 409 normalization, NETWORK_ERROR code. Titles are
// frozen contract items; keep them byte-exact and apostrophe-free.

import { beforeEach, describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../test/server';
import { api, toApiError, TOKEN_KEY, type ApiError } from './client';

/** Replace window.location with a stub that records href assignments. */
const stubWindowLocation = (): void => {
  let currentHref = 'http://localhost:3000/dashboard';
  Object.defineProperty(window, 'location', {
    configurable: true,
    writable: true,
    value: {
      get href() {
        return currentHref;
      },
      set href(value: string) {
        currentHref = value;
      },
      assign: () => undefined,
      reload: () => undefined,
      replace: () => undefined
    }
  });
};

/** Run a request expecting rejection and return the normalized error. */
const expectRejection = async (run: () => Promise<unknown>): Promise<ApiError> => {
  try {
    await run();
  } catch (error) {
    return error as ApiError;
  }
  throw new Error('expected the request to reject');
};

describe('api client', () => {
  beforeEach(() => {
    // jsdom cannot navigate: a real location.href write would trigger a
    // navigation attempt that poisons every later test in the file.
    stubWindowLocation();
  });

  it('creates the axios instance from VITE_API_BASE_URL with a 10 second timeout', () => {
    expect(typeof api.defaults.baseURL).toBe('string');
    expect(api.defaults.timeout).toBe(10_000);
    // The env value is read at module load; assert the read path exists.
    const envValue = (
      import.meta.env as Record<string, string | undefined>
    )['VITE_API_BASE_URL'];
    expect(api.defaults.baseURL).toBe((envValue ?? '').trim());
  });

  it('attaches the bearer authorization header when a token is stored', async () => {
    let authorizationHeader: string | null = null;
    server.use(
      http.get('/api/v1/auth/me', ({ request }) => {
        authorizationHeader = request.headers.get('Authorization');
        return HttpResponse.json({ ok: true });
      })
    );
    localStorage.setItem(TOKEN_KEY, 'stored-token');
    await api.get('/api/v1/auth/me');
    expect(authorizationHeader).toBe('Bearer stored-token');
  });

  it('clears the stored token and redirects to /login on a 401 response', async () => {
    server.use(
      http.get('/api/v1/auth/ping', () =>
        HttpResponse.json(
          { detail: 'invalid or expired token', code: 'TOKEN_INVALID', field: null },
          { status: 401 }
        )
      )
    );
    localStorage.setItem(TOKEN_KEY, 'stale-token');
    const error = await expectRejection(() => api.get('/api/v1/auth/ping'));
    expect(error.status).toBe(401);
    expect(error.code).toBe('TOKEN_INVALID');
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(window.location.href).toBe('/login');
  });

  it('normalizes a 409 backend error preserving code detail and field', async () => {
    server.use(
      http.post('/api/v1/auth/register', () =>
        HttpResponse.json(
          { detail: 'email already registered', code: 'DUPLICATE_EMAIL', field: 'email' },
          { status: 409 }
        )
      )
    );
    const error = await expectRejection(() =>
      api.post('/api/v1/auth/register', { email: 'a@b.co', username: 'abc', password: 'password1' })
    );
    expect(error).toEqual({
      status: 409,
      code: 'DUPLICATE_EMAIL',
      message: 'email already registered',
      field: 'email'
    });
    // Normalization is idempotent for already-normalized values.
    expect(toApiError(error)).toEqual(error);
  });

  it('normalizes a network failure to the NETWORK_ERROR code', async () => {
    server.use(
      http.get('/api/v1/auth/ping', () => {
        return HttpResponse.error();
      })
    );
    const error = await expectRejection(() => api.get('/api/v1/auth/ping'));
    expect(error.code).toBe('NETWORK_ERROR');
    expect(error.status).toBe(0);
    expect(error.message.length).toBeGreaterThan(0);
  });
});

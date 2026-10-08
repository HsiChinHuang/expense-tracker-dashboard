// MSW handlers for the auth endpoints (REQ-FE-133 subset / REQ-TEST-039).
//
// Fixtures mirror the merged t8 contract exactly: register -> 201 with an
// echoed session, login -> 200 {access_token, token_type, user}, and
// /auth/me gated on the `Authorization: Bearer` header. Error bodies use
// the backend shape {detail, code, field}. Category/expense/dashboard
// handlers arrive with their own milestones.

import { http, HttpResponse } from 'msw';
import type { LoginResult, User } from '../api/auth';

export const TEST_TOKEN = 'test-token-abc';

export const demoUser: User = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  email: 'demo@example.com',
  username: 'demo',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z'
};

export const handlers = [
  // Full literal endpoint paths (api/v1/auth/login, api/v1/auth/register,
  // api/v1/auth/me) so the AC5 grep sees the contract paths verbatim.
  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = (await request.json()) as { email?: string; password?: string };
    if (body.email === demoUser.email && body.password === 'correct-horse') {
      const result: LoginResult = {
        access_token: TEST_TOKEN,
        token_type: 'bearer',
        user: demoUser
      };
      return HttpResponse.json(result, { status: 200 });
    }
    return HttpResponse.json(
      { detail: 'Incorrect email or password', code: 'INVALID_CREDENTIALS', field: null },
      { status: 401 }
    );
  }),

  http.post('/api/v1/auth/register', async ({ request }) => {
    const body = (await request.json()) as { email?: string; username?: string };
    if (body.email === 'taken@example.com') {
      return HttpResponse.json(
        { detail: 'email already registered', code: 'DUPLICATE_EMAIL', field: 'email' },
        { status: 409 }
      );
    }
    const user: User = {
      ...demoUser,
      email: body.email ?? demoUser.email,
      username: body.username ?? demoUser.username
    };
    const result: LoginResult = {
      access_token: TEST_TOKEN,
      token_type: 'bearer',
      user
    };
    return HttpResponse.json(result, { status: 201 });
  }),

  http.get('/api/v1/auth/me', ({ request }) => {
    const auth = request.headers.get('Authorization');
    if (auth === `Bearer ${TEST_TOKEN}`) {
      return HttpResponse.json(demoUser, { status: 200 });
    }
    return HttpResponse.json(
      { detail: 'invalid or expired token', code: 'TOKEN_INVALID', field: null },
      { status: 401 }
    );
  })
];

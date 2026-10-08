// AC4: LoginPage — login flow, inline backend error, client-side
// validation short-circuit, register link. Titles are frozen contract items.

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '../test/server';
import { AuthProvider } from '../context/auth_context';
import { LoginPage } from './login_page';

let loginHandlerCalls = 0;

const renderLogin = (entryPath = '/login'): void => {
  loginHandlerCalls = 0;
  server.use(
    http.post('/api/v1/auth/login', async ({ request }) => {
      loginHandlerCalls += 1;
      const body = (await request.json()) as { email?: string; password?: string };
      if (body.email === 'demo@example.com' && body.password === 'correct-horse') {
        return HttpResponse.json({
          access_token: 'test-token-abc',
          token_type: 'bearer',
          user: {
            id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            email: 'demo@example.com',
            username: 'demo',
            is_active: true,
            created_at: '2026-01-01T00:00:00Z'
          }
        });
      }
      return HttpResponse.json(
        { detail: 'Incorrect email or password', code: 'INVALID_CREDENTIALS', field: null },
        { status: 401 }
      );
    })
  );
  render(
    <MemoryRouter initialEntries={[entryPath]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<span>register screen</span>} />
          <Route path="/" element={<span>landing body</span>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
};

const fillLoginForm = (email: string, password: string): void => {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: password } });
  fireEvent.click(screen.getByRole('button', { name: 'Log in' }));
};

describe('LoginPage', () => {
  it('logs in and navigates to the landing route', async () => {
    renderLogin();
    fillLoginForm('demo@example.com', 'correct-horse');
    expect(await screen.findByText('landing body')).toBeTruthy();
    expect(localStorage.getItem('token')).toBe('test-token-abc');
  });

  it('shows the backend 401 message inline on failed login', async () => {
    renderLogin();
    fillLoginForm('demo@example.com', 'wrong-password');
    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toBe('Incorrect email or password');
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('blocks client-side validation before any network request', async () => {
    renderLogin();
    fillLoginForm('not-an-email', 'x');
    expect(await screen.findByText('Enter a valid email')).toBeTruthy();
    // Give any (incorrectly fired) request time to reach the MSW handler.
    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 150);
    });
    expect(loginHandlerCalls).toBe(0);
  });

  it('links to the register page', async () => {
    renderLogin();
    fireEvent.click(screen.getByRole('link', { name: 'Register' }));
    expect(await screen.findByText('register screen')).toBeTruthy();
  });
});

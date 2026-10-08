// AC4: RegisterPage — register + auto-login, field-level 409 mapping,
// on-blur client-side validation without network, login link. Titles are
// frozen contract items.

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { http, HttpResponse } from 'msw';
import { server } from '../test/server';
import { AuthProvider } from '../context/auth_context';
import { RegisterPage } from './register_page';

let registerHandlerCalls = 0;

const renderRegister = (entryPath = '/register'): void => {
  registerHandlerCalls = 0;
  server.use(
    http.post('/api/v1/auth/register', async ({ request }) => {
      registerHandlerCalls += 1;
      const body = (await request.json()) as { email?: string; username?: string };
      if (body.email === 'taken@example.com') {
        return HttpResponse.json(
          { detail: 'email already registered', code: 'DUPLICATE_EMAIL', field: 'email' },
          { status: 409 }
        );
      }
      return HttpResponse.json({
        access_token: 'test-token-abc',
        token_type: 'bearer',
        user: {
          id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
          email: body.email ?? 'new@example.com',
          username: body.username ?? 'newuser',
          is_active: true,
          created_at: '2026-01-01T00:00:00Z'
        }
      });
    })
  );
  render(
    <MemoryRouter initialEntries={[entryPath]}>
      <AuthProvider>
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<span>login screen</span>} />
          <Route path="/" element={<span>landing body</span>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
};

const fillRegisterForm = (email: string, username: string, password: string): void => {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } });
  fireEvent.change(screen.getByLabelText('Username'), { target: { value: username } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: password } });
  fireEvent.change(screen.getByLabelText('Confirm password'), { target: { value: password } });
  fireEvent.click(screen.getByRole('button', { name: 'Register' }));
};

describe('RegisterPage', () => {
  it('registers and auto-logs-in on success', async () => {
    renderRegister();
    fillRegisterForm('new@example.com', 'newuser', 'password1');
    expect(await screen.findByText('landing body')).toBeTruthy();
    expect(localStorage.getItem('token')).toBe('test-token-abc');
  });

  it('surfaces the backend 409 error on the email field', async () => {
    renderRegister();
    fillRegisterForm('taken@example.com', 'newuser', 'password1');
    const fieldError = await screen.findByText('email already registered');
    expect(fieldError.getAttribute('id')).toBe('register-email-error');
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('validates password and username rules on blur without a network call', async () => {
    renderRegister();
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'short' } });
    fireEvent.blur(screen.getByLabelText('Password'));
    expect(await screen.findByText('Password must be at least 8 characters')).toBeTruthy();

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'a b' } });
    fireEvent.blur(screen.getByLabelText('Username'));
    expect(await screen.findByText('Username must not contain whitespace')).toBeTruthy();

    // The submit was never attempted: the flag-flipping handler never ran.
    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 150);
    });
    expect(registerHandlerCalls).toBe(0);
  });

  it('links to the login page', async () => {
    renderRegister();
    fireEvent.click(screen.getByRole('link', { name: 'Log in' }));
    expect(await screen.findByText('login screen')).toBeTruthy();
  });
});

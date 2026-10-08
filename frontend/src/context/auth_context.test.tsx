// AC2: AuthContext — mount-time token validation, login/register storage,
// logout cleanup. Titles are frozen contract items.

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './auth_context';
import { TOKEN_KEY } from '../api/client';
import { demoUser } from '../test/handlers';

/** Render the provider plus a probe component exercising the hook. */
const renderAuth = (): void => {
  render(
    <AuthProvider>
      <Probe />
    </AuthProvider>
  );
};

const Probe = (): JSX.Element => {
  const auth = useAuth();
  return (
    <div>
      <span>{auth.isLoading ? 'loading' : 'idle'}</span>
      <span data-testid="username">{auth.user?.username ?? 'none'}</span>
      <span data-testid="token">{auth.token ?? 'none'}</span>
      <button
        type="button"
        onClick={() => {
          void auth
            .login({ email: demoUser.email, password: 'correct-horse' })
            .catch(() => undefined);
        }}
      >
        do-login
      </button>
      <button
        type="button"
        onClick={() => {
          void auth
            .register({ email: 'new@example.com', username: 'newuser', password: 'password1' })
            .catch(() => undefined);
        }}
      >
        do-register
      </button>
      <button type="button" onClick={auth.logout}>
        do-logout
      </button>
    </div>
  );
};

describe('AuthProvider', () => {
  it('populates the user from /auth/me when a stored token is valid', async () => {
    localStorage.setItem(TOKEN_KEY, 'test-token-abc');
    renderAuth();
    expect(screen.getByText('loading')).toBeTruthy();
    expect(await screen.findByText('idle')).toBeTruthy();
    expect(screen.getByTestId('username').textContent).toBe(demoUser.username);
    expect(screen.getByTestId('token').textContent).toBe('test-token-abc');
  });

  it('removes an invalid stored token and stays logged out', async () => {
    localStorage.setItem(TOKEN_KEY, 'expired-token');
    renderAuth();
    expect(await screen.findByText('idle')).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByTestId('username').textContent).toBe('none');
    });
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(screen.getByTestId('token').textContent).toBe('none');
  });

  it('stores the token and user on login', async () => {
    renderAuth();
    await screen.findByText('idle');
    fireEvent.click(screen.getByRole('button', { name: 'do-login' }));
    await waitFor(() => {
      expect(screen.getByTestId('username').textContent).toBe(demoUser.username);
    });
    expect(localStorage.getItem(TOKEN_KEY)).toBe('test-token-abc');
    expect(screen.getByTestId('token').textContent).toBe('test-token-abc');
  });

  it('registers then auto-logs-in with the returned token', async () => {
    renderAuth();
    await screen.findByText('idle');
    fireEvent.click(screen.getByRole('button', { name: 'do-register' }));
    await waitFor(() => {
      expect(screen.getByTestId('username').textContent).toBe('newuser');
    });
    expect(localStorage.getItem(TOKEN_KEY)).toBe('test-token-abc');
  });

  it('clears the stored token and user on logout', async () => {
    renderAuth();
    await screen.findByText('idle');
    fireEvent.click(screen.getByRole('button', { name: 'do-login' }));
    await waitFor(() => {
      expect(screen.getByTestId('username').textContent).toBe(demoUser.username);
    });
    fireEvent.click(screen.getByRole('button', { name: 'do-logout' }));
    await waitFor(() => {
      expect(screen.getByTestId('username').textContent).toBe('none');
    });
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(screen.getByTestId('token').textContent).toBe('none');
  });
});

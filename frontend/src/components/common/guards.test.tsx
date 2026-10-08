// AC3: route guards — ProtectedRoute / PublicOnlyRoute behavior and the
// router-state preservation contract. Titles are frozen contract items.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import type { ReactNode } from 'react';
import { AuthProvider } from '../../context/auth_context';
import { ProtectedRoute } from './protected_route';
import { PublicOnlyRoute } from './public_only_route';

const renderGuards = (ui: ReactNode, entryPath = '/'): void => {
  render(<MemoryRouter initialEntries={[entryPath]}>{ui}</MemoryRouter>);
};

const LocationProbe = (): JSX.Element => {
  const location = useLocation();
  return <span data-testid="location">{JSON.stringify(location.state ?? null)}</span>;
};

const authedTree = (children: ReactNode): JSX.Element => (
  <AuthProvider>{children}</AuthProvider>
);

describe('route guards', () => {
  it('redirects an unauthenticated visit to a protected route to /login', () => {
    renderGuards(
      authedTree(
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<span>home body</span>} />
          </Route>
          <Route path="/login" element={<span>login screen</span>} />
        </Routes>
      ),
      '/'
    );
    expect(screen.getByText('login screen')).toBeTruthy();
  });

  it('renders protected content for an authenticated session', async () => {
    localStorage.setItem('token', 'test-token-abc');
    renderGuards(
      authedTree(
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<span>home body</span>} />
          </Route>
        </Routes>
      ),
      '/'
    );
    // While /auth/me validates, the full-page spinner is shown first.
    expect(screen.getByRole('status')).toBeTruthy();
    expect(await screen.findByText('home body')).toBeTruthy();
    expect(screen.queryByRole('status')).toBeNull();
  });

  it('redirects a logged-in visitor from /login to /', async () => {
    localStorage.setItem('token', 'test-token-abc');
    renderGuards(
      authedTree(
        <Routes>
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<span>login screen</span>} />
          </Route>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<span>home body</span>} />
          </Route>
        </Routes>
      ),
      '/login'
    );
    expect(await screen.findByText('home body')).toBeTruthy();
  });

  it('shows a full-page spinner while the auth state is loading', () => {
    localStorage.setItem('token', 'test-token-abc');
    renderGuards(
      authedTree(
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<span>home body</span>} />
          </Route>
        </Routes>
      ),
      '/'
    );
    const status = screen.getByRole('status');
    expect(status.textContent).toContain('Loading');
  });

  it('preserves the attempted location in router state on redirect', () => {
    renderGuards(
      authedTree(
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<span>dashboard body</span>} />
          </Route>
          <Route
            path="/login"
            element={
              <>
                <span>login screen</span>
                <LocationProbe />
              </>
            }
          />
        </Routes>
      ),
      '/dashboard'
    );
    const probe = screen.getByTestId('location');
    const state = JSON.parse(probe.textContent ?? '{}') as { from?: { pathname?: string } };
    expect(state.from?.pathname).toBe('/dashboard');
  });
});

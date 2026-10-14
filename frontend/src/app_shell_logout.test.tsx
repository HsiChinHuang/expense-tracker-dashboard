// t61 ac2 — the sign-out control works on EVERY shell-wrapped page, proved
// on the REAL route table.
//
// Every test below mounts the merged `App` from ./app (NOT a hand-built
// route tree) under MemoryRouter, first awaits the shell header's logout
// button with findByTestId (the shell mounts asynchronously behind the auth
// guard), then re-reads it with getByTestId, clicks it, and asserts the
// session really ended: the stored token is gone from localStorage and the
// merged login page heading is what the carried guard redirects to. The
// dashboard route also gets the six carried dashboard endpoint fixtures so
// the page under the shell settles quietly.
//
// The last test proves the other half of the placement claim: on /login the
// shell does not survive the logout, so the button must be ABSENT there.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState, type ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { server } from './test/server';
import { TEST_TOKEN } from './test/handlers';
import { App } from './app';
import { MonthProvider } from './context/month_context';
import { AuthProvider } from './context/auth_context';
import { ToastProvider } from './context/toast_context';

/** Fixtures for the six dashboard endpoints the "/" page mounts. */
const registerDashboardFixtures = (): void => {
  server.use(
    http.get('/api/v1/dashboard/summary', () =>
      HttpResponse.json({
        year_month: '2026-02',
        total: '0.00',
        budget_amount: '0.00',
        remaining: '0.00',
        percentage: null,
        is_over_budget: false,
        category_count: 0
      })
    ),
    http.get('/api/v1/dashboard/by-category', () =>
      HttpResponse.json({ year_month: '2026-02', total: '0.00', categories: [] })
    ),
    http.get('/api/v1/dashboard/trend', () => HttpResponse.json({ months: [] })),
    http.get('/api/v1/dashboard/cumulative', () =>
      HttpResponse.json({ year_month: '2026-02', budget: '0.00', days: [] })
    ),
    http.get('/api/v1/dashboard/heatmap', () =>
      HttpResponse.json({ max_amount: '0.00', weeks: [] })
    ),
    http.get('/api/v1/dashboard/recent', () => HttpResponse.json({ items: [] }))
  );
};

const AppTree = ({ children }: { children: ReactNode }): JSX.Element => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return (
    <QueryClientProvider client={client}>
      <MonthProvider>
        <AuthProvider>
          <ToastProvider>{children}</ToastProvider>
        </AuthProvider>
      </MonthProvider>
    </QueryClientProvider>
  );
};

/** Mount the REAL merged App at `path` with an authenticated session. */
const mountAt = (path: string): void => {
  localStorage.setItem('token', TEST_TOKEN);
  render(
    <AppTree>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </AppTree>
  );
};

/**
 * Click the header sign-out control and prove the session ended on the
 * merged login page — the carried guard owns the redirect, this test only
 * observes it.
 */
const expectLogoutWorks = async (): Promise<void> => {
  const button = await screen.findByTestId('logout-button');
  // The testid contract: the same node is reachable synchronously too.
  expect(screen.getByTestId('logout-button')).toBe(button);
  fireEvent.click(button);
  expect(localStorage.getItem('token')).toBeNull();
  expect(await screen.findByRole('heading', { name: 'Log in' })).toBeTruthy();
  // The shell did not survive the redirect.
  expect(screen.queryByTestId('logout-button')).toBeNull();
};

beforeEach(() => {
  server.resetHandlers();
});

describe('sign-out control in the shell header (t61 ac2)', () => {
  it('the header button signs the session out on /', async () => {
    registerDashboardFixtures();
    mountAt('/');
    await expectLogoutWorks();
  });

  it('the header button signs the session out on /expenses', async () => {
    mountAt('/expenses');
    await expectLogoutWorks();
  });

  it('the header button signs the session out on /budgets', async () => {
    mountAt('/budgets');
    await expectLogoutWorks();
  });

  it('the header button signs the session out on /categories', async () => {
    mountAt('/categories');
    await expectLogoutWorks();
  });
});

describe('the control lives in the shell only (t61 ac2)', () => {
  it('the login page renders no shell and no logout control', async () => {
    // A signed-out visit to /login renders the merged login page directly:
    // no shell header, hence no logout button anywhere on the page.
    render(
      <AppTree>
        <MemoryRouter initialEntries={['/login']}>
          <App />
        </MemoryRouter>
      </AppTree>
    );
    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeTruthy();
    expect(screen.queryByTestId('logout-button')).toBeNull();
  });
});

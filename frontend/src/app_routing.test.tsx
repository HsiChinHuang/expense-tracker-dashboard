// t60 ac2 — the shell survives navigation, proved on the REAL route table
// (REQ-FE-010, REQ-FE-011).
//
// Every test below mounts the merged `App` from ../app (NOT a hand-built
// route tree) under MemoryRouter. The defect this card fixes is that
// /expenses, /budgets and /categories hung as SIBLINGS of the AppShell
// route, so the header vanished on those pages; the fix re-nests them as
// children of `<Route path="/" element={<AppShell />}>`. A hand-built tree
// could not prove the merged table is nested, so it is not used here.
//
// The unknown route covers the new catch-all: it sits OUTSIDE the
// ProtectedRoute block, so an unknown path renders the 404 page (title
// "Not Found" + the "Back to Dashboard" link) instead of being redirected
// to /login.
//
// The auth session is the merged localStorage-token convention, and the
// merged msw fixtures (test/handlers.ts, byte-identical) already answer
// every request the three feature pages make — no test infrastructure is
// extended here.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { useState, type ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { server } from './test/server';
import { TEST_TOKEN } from './test/handlers';
import { App } from './app';
import { MonthProvider } from './context/month_context';
import { AuthProvider } from './context/auth_context';
import { ToastProvider } from './context/toast_context';

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

/** The four guard-wrapped NavLink entries the t60 shell header must render. */
const shellNavLinkNames = ['Dashboard', 'Expenses', 'Budget', 'Categories'];

/** The AppShell header node — brand heading plus its four NavLink entries. */
const expectShellHeader = async (): Promise<void> => {
  const heading = await screen.findByRole('heading', { name: 'Expense Tracker' });
  expect(heading.tagName).toBe('H1');
  // The shell's nav is present on the page too: every guard-wrapped NavLink
  // (app_shell.tsx's module-local wrapper) renders as a real link once a
  // router context exists — including the 4th entry added by t60.
  for (const name of shellNavLinkNames) {
    expect(await screen.findByRole('link', { name })).toBeTruthy();
  }
};

beforeEach(() => {
  server.resetHandlers();
  document.title = '';
});

describe('shell survives navigation (ac1/ac2, REQ-FE-010)', () => {
  it('the shell header is rendered on /expenses', async () => {
    mountAt('/expenses');
    await expectShellHeader();
    // The page content sits INSIDE the shell, not next to it.
    expect(await screen.findByRole('heading', { name: 'Expenses', level: 1 }))
      .toBeTruthy();
  });

  it('the shell header is rendered on /budgets', async () => {
    mountAt('/budgets');
    await expectShellHeader();
    expect(await screen.findByRole('heading', { name: 'Budget', level: 1 }))
      .toBeTruthy();
  });

  it('the shell header is rendered on /categories', async () => {
    mountAt('/categories');
    await expectShellHeader();
    expect(
      await screen.findByRole('heading', { name: 'Categories', level: 1 })
    ).toBeTruthy();
  });
});

describe('catch-all route (ac1/ac2, REQ-FE-011)', () => {
  it('an unknown route renders the Not Found page with its back link', async () => {
    mountAt('/unknown-route');
    expect(await screen.findByRole('heading', { name: 'Not Found' })).toBeTruthy();
    const back = await screen.findByRole('link', { name: 'Back to Dashboard' });
    expect(back.getAttribute('href')).toBe('/');
    // The catch-all is a sibling of the protected block, so the auth guard
    // never redirects an unknown path to /login.
    expect(screen.queryByRole('heading', { name: 'Log in' })).toBeNull();
    await expect(
      screen.findByRole('heading', { name: 'Not Found' })
    ).resolves.toBeTruthy();
    expect(document.title).toBe('Not Found');
  });
});

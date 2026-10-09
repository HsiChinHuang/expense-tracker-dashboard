// AC1: dashboard route + nav wiring (REQ-FE-010/012/015, REQ-FE-062 — t22).
// Two frozen nodes mounting the REAL merged App route table: "/" renders
// the AppShell with DashboardPage in its outlet inside ProtectedRoute, the
// document title is exactly "Dashboard", and the shell's Dashboard nav link
// points at "/". The auth session is the merged localStorage-token
// convention; the six dashboard endpoints get per-test server.use fixtures
// (handlers.ts is byte-identical and carries no dashboard fixtures).

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState, type ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { server } from '../test/server';
import { TEST_TOKEN, resetCallCounts } from '../test/handlers';
import { App } from '../app';
import { MonthProvider } from '../context/month_context';
import { AuthProvider } from '../context/auth_context';
import { ToastProvider } from '../context/toast_context';

/** Log every summary request so "the dashboard mounted" is handler-proven. */
const summaryRequests: string[] = [];

const registerFixtures = (): void => {
  server.use(
    http.get('/api/v1/dashboard/summary', ({ request }) => {
      const yearMonth = new URL(request.url).searchParams.get('year_month') ?? '';
      summaryRequests.push(yearMonth);
      return HttpResponse.json(
        {
          year_month: yearMonth,
          total: '125.50',
          budget_amount: '2000.00',
          remaining: '1874.50',
          percentage: 6.3,
          is_over_budget: false,
          category_count: 2
        },
        { status: 200 }
      );
    }),
    http.get('/api/v1/dashboard/by-category', ({ request }) =>
      HttpResponse.json(
        {
          year_month: new URL(request.url).searchParams.get('year_month') ?? '',
          total: '0.00',
          categories: []
        },
        { status: 200 }
      )
    ),
    http.get('/api/v1/dashboard/trend', () => HttpResponse.json({ months: [] }, { status: 200 })),
    http.get('/api/v1/dashboard/cumulative', ({ request }) =>
      HttpResponse.json(
        {
          year_month: new URL(request.url).searchParams.get('year_month') ?? '',
          budget: '0.00',
          days: []
        },
        { status: 200 }
      )
    ),
    http.get('/api/v1/dashboard/heatmap', () =>
      HttpResponse.json({ max_amount: '0.00', weeks: [] }, { status: 200 })
    ),
    http.get('/api/v1/dashboard/recent', () => HttpResponse.json({ items: [] }, { status: 200 }))
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

const renderAtRoot = (): void => {
  render(
    <AppTree>
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    </AppTree>
  );
};

beforeEach(() => {
  summaryRequests.length = 0;
  resetCallCounts();
  registerFixtures();
});

describe('dashboard route wiring (ac1)', () => {
  it('the authenticated shell mounts the dashboard with its document title', async () => {
    localStorage.setItem('token', TEST_TOKEN);
    renderAtRoot();
    // The shell AND the dashboard content render together at "/".
    expect(await screen.findByText('Expense Tracker')).toBeTruthy();
    expect(await screen.findByTestId('kpi-total')).toBeTruthy();
    expect(summaryRequests.length).toBeGreaterThan(0);
    // The old landing placeholder is gone (replaced by the outlet).
    expect(screen.queryByText('Frontend skeleton is running.')).toBeNull();
    // REQ-FE-015: the document title is exactly "Dashboard".
    await waitFor(() => {
      expect(document.title).toBe('Dashboard');
    });
  });

  it('the shell navigation links to the dashboard', async () => {
    localStorage.setItem('token', TEST_TOKEN);
    renderAtRoot();
    expect(await screen.findByTestId('kpi-total')).toBeTruthy();
    const link = screen.getByRole('link', { name: 'Dashboard' });
    expect(link.getAttribute('href')).toBe('/');
  });
});

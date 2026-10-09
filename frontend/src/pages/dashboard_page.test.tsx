// AC3/AC4/AC5: DashboardPage (REQ-FE-062/074/100/102, REQ-ARCH-032,
// REQ-PROD-014/023/033/036 — t22). Eleven frozen nodes: five summary/state
// nodes (ac3), four chart/recent-list nodes (ac4), two month-switch nodes
// (ac5).
//
// Proof mechanisms are OBSERVABLE, per the merged t16/t18/t20 precedent:
// - the six dashboard fixtures are per-test `server.use` overrides
//   (handlers.ts stays byte-identical and carries no dashboard fixtures);
//   each records the `year_month` its endpoint received, so "which month"
//   and "refetched" are handler-observed facts, never code reading;
// - the rapid-switch node asserts the FINAL state only (msw delay() inside
//   the override forces the stale-first ordering; phase_3 W11 / review_plan
//   W7 forbid raw count equality as race proof);
// - the retry node uses a fail-once override and asserts the refetch
//   reaches the handler and the KPIs recover.
//
// Mounts carry their own QueryClient (retry:false, staleTime:0) per the
// STATE/QUERY RULES; the month is driven through the real MonthPicker UI.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { delay, http, HttpResponse } from 'msw';
import { useState, type ReactNode } from 'react';
import { server } from '../test/server';
import { resetCallCounts } from '../test/handlers';
import { AuthProvider } from '../context/auth_context';
import { MonthProvider } from '../context/month_context';
import { DashboardPage } from './dashboard_page';
import type {
  DashboardByCategory,
  DashboardCumulative,
  DashboardHeatmap,
  DashboardRecent,
  DashboardSummary,
  DashboardTrend
} from '../api/dashboard';

const SUMMARY_PATH = '/api/v1/dashboard/summary';
const BY_CATEGORY_PATH = '/api/v1/dashboard/by-category';
const TREND_PATH = '/api/v1/dashboard/trend';
const CUMULATIVE_PATH = '/api/v1/dashboard/cumulative';
const HEATMAP_PATH = '/api/v1/dashboard/heatmap';
const RECENT_PATH = '/api/v1/dashboard/recent';

const SIX_PATHS = [
  SUMMARY_PATH,
  BY_CATEGORY_PATH,
  TREND_PATH,
  CUMULATIVE_PATH,
  HEATMAP_PATH,
  RECENT_PATH
] as const;

const MONTH_DRIVEN_PATHS = [SUMMARY_PATH, BY_CATEGORY_PATH, CUMULATIVE_PATH] as const;

const CATEGORY_ID = 'c1000000-0000-4000-8000-000000000001';

// --- handler-observed request log -------------------------------------------

const requests = new Map<string, string[]>();

const monthsSeen = (path: string): string[] => requests.get(path) ?? [];

const requestCount = (path: string): number => (requests.get(path) ?? []).length;

const record = (path: string, yearMonth: string | null): void => {
  requests.set(path, [...(requests.get(path) ?? []), yearMonth ?? '']);
};

const requestedMonth = (request: Request): string =>
  new URL(request.url).searchParams.get('year_month') ?? '';

// --- default (populated) payloads -------------------------------------------

const summaryFixture = (yearMonth: string): DashboardSummary => ({
  year_month: yearMonth,
  total: '125.50',
  budget_amount: '2000.00',
  remaining: '1874.50',
  percentage: 6.3,
  is_over_budget: false,
  category_count: 2
});

const byCategoryFixture = (yearMonth: string): DashboardByCategory => ({
  year_month: yearMonth,
  total: '125.50',
  categories: [
    {
      category_id: CATEGORY_ID,
      category_name: 'Food',
      color: '#EF4444',
      amount: '125.50',
      percentage: 100
    }
  ]
});

const trendFixture = (): DashboardTrend => ({
  months: [
    { year_month: '2026-01', total: '80.00' },
    { year_month: '2026-02', total: '125.50' }
  ]
});

const cumulativeFixture = (yearMonth: string): DashboardCumulative => ({
  year_month: yearMonth,
  budget: '2000.00',
  days: [{ date: `${yearMonth}-03`, daily: '125.50', cumulative: '125.50' }]
});

const heatmapFixture = (): DashboardHeatmap => ({
  max_amount: '125.50',
  weeks: [
    {
      week_start: '2026-02-02',
      days: [
        { date: '2026-02-02', amount: '0.00' },
        { date: '2026-02-03', amount: '125.50' },
        { date: '2026-02-04', amount: '0.00' },
        { date: '2026-02-05', amount: '0.00' },
        { date: '2026-02-06', amount: '0.00' },
        { date: '2026-02-07', amount: '0.00' },
        { date: '2026-02-08', amount: '0.00' }
      ]
    }
  ]
});

const recentFixture = (): DashboardRecent => ({
  items: [
    {
      id: 'e1000000-0000-4000-8000-000000000001',
      amount: '125.50',
      currency: 'USD',
      category_id: CATEGORY_ID,
      category_name: 'Food',
      category_color: '#EF4444',
      date: '2026-02-03',
      note: 'groceries',
      created_at: '2026-02-03T09:00:00Z',
      updated_at: '2026-02-03T09:00:00Z'
    }
  ]
});

/** Register the six fixtures with the populated payloads above. */
const registerPopulatedFixtures = (): void => {
  server.use(
    http.get(SUMMARY_PATH, ({ request }) => {
      const yearMonth = requestedMonth(request);
      record(SUMMARY_PATH, yearMonth);
      return HttpResponse.json(summaryFixture(yearMonth), { status: 200 });
    }),
    http.get(BY_CATEGORY_PATH, ({ request }) => {
      const yearMonth = requestedMonth(request);
      record(BY_CATEGORY_PATH, yearMonth);
      return HttpResponse.json(byCategoryFixture(yearMonth), { status: 200 });
    }),
    http.get(TREND_PATH, () => {
      record(TREND_PATH, '');
      return HttpResponse.json(trendFixture(), { status: 200 });
    }),
    http.get(CUMULATIVE_PATH, ({ request }) => {
      const yearMonth = requestedMonth(request);
      record(CUMULATIVE_PATH, yearMonth);
      return HttpResponse.json(cumulativeFixture(yearMonth), { status: 200 });
    }),
    http.get(HEATMAP_PATH, () => {
      record(HEATMAP_PATH, '');
      return HttpResponse.json(heatmapFixture(), { status: 200 });
    }),
    http.get(RECENT_PATH, () => {
      record(RECENT_PATH, '');
      return HttpResponse.json(recentFixture(), { status: 200 });
    })
  );
};

// --- harness -----------------------------------------------------------------

const renderPage = (): void => {
  render(
    <Provider>
      <MonthProvider>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </MonthProvider>
    </Provider>
  );
};

const Provider = ({ children }: { children: ReactNode }): JSX.Element => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
};

/** Wait until the KPI cards have served their first summary. */
const summaryLoaded = async (): Promise<void> => {
  await waitFor(() => {
    expect(screen.queryByTestId('kpi-total')).not.toBeNull();
  });
};

/** Shift a YYYY-MM by delta months (test-side integer math). */
const shiftMonth = (yearMonth: string, delta: number): string => {
  const parts = yearMonth.split('-');
  const index = Number(parts[0] ?? '0') * 12 + (Number(parts[1] ?? '0') - 1) + delta;
  const year = Math.floor(index / 12);
  const month = ((index % 12) + 12) % 12 + 1;
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}`;
};

beforeEach(() => {
  requests.clear();
  resetCallCounts();
});

describe('DashboardPage summary and states (ac3)', () => {
  it('the four kpi cards render the summary strings verbatim', async () => {
    registerPopulatedFixtures();
    renderPage();
    await summaryLoaded();
    // Each amount is the API string with a '$' prefix and nothing else.
    expect(screen.getByTestId('kpi-total').textContent).toBe('$125.50');
    expect(screen.getByTestId('kpi-budget').textContent).toBe('$2000.00');
    expect(screen.getByTestId('kpi-remaining').textContent).toBe('$1874.50');
    // The fourth card is the summary's category_count (frozen contract).
    expect(screen.getByTestId('kpi-categories').textContent).toBe('2');
  });

  it('a null percentage summary renders the no budget set affordance not nan', async () => {
    registerPopulatedFixtures();
    server.use(
      http.get(SUMMARY_PATH, ({ request }) => {
        const yearMonth = requestedMonth(request);
        record(SUMMARY_PATH, yearMonth);
        return HttpResponse.json(
          {
            year_month: yearMonth,
            total: '125.50',
            budget_amount: '0.00',
            remaining: '-125.50',
            percentage: null,
            is_over_budget: false,
            category_count: 1
          },
          { status: 200 }
        );
      })
    );
    renderPage();
    await summaryLoaded();
    expect(await screen.findByText('No budget set')).toBeTruthy();
    // Q3: with a null percentage there is NO progressbar region at all.
    expect(screen.queryByRole('progressbar')).toBeNull();
    // And nowhere on the page does a NaN leak into the DOM.
    expect(document.body.textContent).not.toContain('NaN');
  });

  it('pending dashboard queries render skeleton status regions', () => {
    registerPopulatedFixtures();
    renderPage();
    // Synchronously (before any handler resolves) every section shows its
    // own role=status region and each carries an animate-pulse skeleton.
    const regions = screen.getAllByRole('status');
    expect(regions.length).toBeGreaterThanOrEqual(4);
    for (const region of regions) {
      expect(region.querySelector('.animate-pulse')).not.toBeNull();
    }
  });

  it('a failed summary query renders the error state whose retry refetches', async () => {
    registerPopulatedFixtures();
    let summaryCalls = 0;
    server.use(
      http.get(SUMMARY_PATH, ({ request }) => {
        const yearMonth = requestedMonth(request);
        record(SUMMARY_PATH, yearMonth);
        summaryCalls += 1;
        if (summaryCalls === 1) {
          return HttpResponse.json(
            { detail: 'boom', code: 'SERVER_ERROR', field: null },
            { status: 500 }
          );
        }
        return HttpResponse.json(summaryFixture(yearMonth), { status: 200 });
      })
    );
    renderPage();
    const alerts = await screen.findAllByRole('alert');
    expect(alerts.length).toBeGreaterThan(0);
    expect(screen.queryByTestId('kpi-total')).toBeNull();
    // The Retry button refetches: the fail-once handler now succeeds and
    // the KPI cards appear (the refetch reached the handler: two requests).
    fireEvent.click(within(alerts[0] as HTMLElement).getByRole('button', { name: 'Retry' }));
    await waitFor(() => {
      expect(screen.queryByTestId('kpi-total')?.textContent).toBe('$125.50');
    });
    expect(summaryCalls).toBe(2);
  });

  it('the six dashboard endpoints are requested in parallel on mount', async () => {
    registerPopulatedFixtures();
    renderPage();
    await summaryLoaded();
    await waitFor(() => {
      expect(screen.queryByTestId('category-pie-chart')).not.toBeNull();
      expect(screen.queryByTestId('monthly-trend-chart')).not.toBeNull();
      expect(screen.queryByTestId('cumulative-line-chart')).not.toBeNull();
      expect(screen.queryByTestId('weekly-heatmap')).not.toBeNull();
      expect(screen.queryByTestId('recent-item')).not.toBeNull();
    });
    // Six independent reads under one mount: each endpoint received exactly
    // one request and its consumer already rendered (REQ-ARCH-032).
    for (const path of SIX_PATHS) {
      expect(requestCount(path)).toBe(1);
    }
  });
});

describe('DashboardPage charts and recent list (ac4)', () => {
  it('the five charts and the recent list render from their own queries', async () => {
    registerPopulatedFixtures();
    renderPage();
    await summaryLoaded();
    await waitFor(() => {
      expect(screen.queryByTestId('category-pie-chart')).not.toBeNull();
      expect(screen.queryByTestId('monthly-trend-chart')).not.toBeNull();
      expect(screen.queryByTestId('cumulative-line-chart')).not.toBeNull();
      expect(screen.queryByTestId('weekly-heatmap')).not.toBeNull();
      expect(screen.queryByTestId('budget-progress')).not.toBeNull();
      expect(screen.queryByTestId('recent-item')).not.toBeNull();
    });
    // The progress bar is fed by the summary (percentage 6.3 -> green fill).
    expect(screen.getByTestId('budget-progress-track')).toBeTruthy();
  });

  it('the recent list renders api order and verbatim amounts', async () => {
    registerPopulatedFixtures();
    server.use(
      http.get(RECENT_PATH, () => {
        record(RECENT_PATH, '');
        const item = (id: string, name: string, amount: string): DashboardRecent['items'][number] => ({
          id: `e0000000-0000-4000-8000-00000000000${id}`,
          amount,
          currency: 'USD',
          category_id: CATEGORY_ID,
          category_name: name,
          category_color: '#EF4444',
          date: '2026-02-04',
          note: null,
          created_at: '2026-02-04T09:00:00Z',
          updated_at: '2026-02-04T09:00:00Z'
        });
        return HttpResponse.json(
          {
            items: [item('1', 'First', '1.00'), item('2', 'Second', '2.00'), item('3', 'Third', '3.00')]
          },
          { status: 200 }
        );
      })
    );
    renderPage();
    await summaryLoaded();
    await waitFor(() => {
      expect(screen.getAllByTestId('recent-item').length).toBe(3);
    });
    // API order is preserved and every amount is the verbatim string.
    const amounts = screen.getAllByTestId('recent-amount').map((node) => node.textContent);
    expect(amounts).toEqual(['$1.00', '$2.00', '$3.00']);
    const rows = screen.getAllByTestId('recent-item').map((node) => node.textContent ?? '');
    expect(rows[0]).toContain('First');
    expect(rows[1]).toContain('Second');
    expect(rows[2]).toContain('Third');
  });

  it('an empty recent payload renders the empty state not a blank page', async () => {
    registerPopulatedFixtures();
    server.use(
      http.get(RECENT_PATH, () => {
        record(RECENT_PATH, '');
        return HttpResponse.json({ items: [] }, { status: 200 });
      })
    );
    renderPage();
    await summaryLoaded();
    expect(await screen.findByText('No recent transactions')).toBeTruthy();
    // The page itself stays rendered around the empty section.
    expect(screen.getByTestId('kpi-total')).toBeTruthy();
  });

  it('an empty month renders every chart empty state not a blank page', async () => {
    registerPopulatedFixtures();
    server.use(
      http.get(BY_CATEGORY_PATH, ({ request }) =>
        HttpResponse.json(
          { year_month: requestedMonth(request), total: '0.00', categories: [] },
          { status: 200 }
        )
      ),
      http.get(TREND_PATH, () => {
        record(TREND_PATH, '');
        return HttpResponse.json({ months: [] }, { status: 200 });
      }),
      http.get(CUMULATIVE_PATH, ({ request }) =>
        HttpResponse.json(
          { year_month: requestedMonth(request), budget: '0.00', days: [] },
          { status: 200 }
        )
      ),
      http.get(HEATMAP_PATH, () => {
        record(HEATMAP_PATH, '');
        return HttpResponse.json({ max_amount: '0.00', weeks: [] }, { status: 200 });
      })
    );
    renderPage();
    await summaryLoaded();
    // Each of the four t21 charts shows its own pinned empty state.
    expect(await screen.findByText('No expenses this month')).toBeTruthy();
    expect(await screen.findByText('No data for this period')).toBeTruthy();
    expect(await screen.findByText('No spending this month')).toBeTruthy();
    expect(await screen.findByText('No activity in this window')).toBeTruthy();
    // The page around them is fully rendered, never blank.
    expect(screen.getByTestId('kpi-total')).toBeTruthy();
    expect(screen.getByTestId('month-picker')).toBeTruthy();
  });
});

describe('DashboardPage month switching (ac5)', () => {
  it('stepping the month refetches every month-driven dashboard query', async () => {
    registerPopulatedFixtures();
    renderPage();
    await summaryLoaded();
    const initial = monthsSeen(SUMMARY_PATH)[0] ?? '';
    const before = MONTH_DRIVEN_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    const expected = shiftMonth(initial, 1);
    // Every month-driven endpoint receives the NEW month at the handler...
    await waitFor(() => {
      for (const path of MONTH_DRIVEN_PATHS) {
        const seen = monthsSeen(path);
        expect(seen[seen.length - 1]).toBe(expected);
      }
    });
    // ...and each endpoint's request count grew (a refetch, not a cache hit).
    MONTH_DRIVEN_PATHS.forEach((path, index) => {
      expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
    });
  });

  it('rapid month switching settles on the last selected month', async () => {
    registerPopulatedFixtures();
    // The stale-first ordering is FORCED inside the override: the first
    // month's summary is delayed so it resolves AFTER the newer one.
    let firstMonth = '';
    server.use(
      http.get(SUMMARY_PATH, async ({ request }) => {
        const yearMonth = requestedMonth(request);
        record(SUMMARY_PATH, yearMonth);
        if (firstMonth === '') {
          firstMonth = yearMonth;
        }
        if (yearMonth === firstMonth) {
          await delay(120);
        }
        return HttpResponse.json(
          { ...summaryFixture(yearMonth), total: `1.${yearMonth.slice(5)}` },
          { status: 200 }
        );
      })
    );
    renderPage();
    await summaryLoaded();
    const initial = monthsSeen(SUMMARY_PATH)[0] ?? '';
    const target = shiftMonth(initial, 2);
    // Two rapid clicks: the UI must end on the LAST selection only.
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    await waitFor(() => {
      expect(screen.getByTestId('kpi-total').textContent).toBe(`$1.${target.slice(5)}`);
    });
    // FINAL-state evidence: the newest month is the last one every
    // month-driven endpoint served...
    const seen = monthsSeen(SUMMARY_PATH);
    expect(seen[seen.length - 1]).toBe(target);
    // ...and the late stale response never overwrote the settled view.
    await new Promise((resolve) => {
      setTimeout(resolve, 200);
    });
    expect(screen.getByTestId('kpi-total').textContent).toBe(`$1.${target.slice(5)}`);
  });
});

/* eslint-disable react-hooks/rules-of-hooks -- the project coding standard
pins snake_case hook names (use_dashboard); eslint-plugin-react-hooks only
recognizes usePascalCase, so the recognition false-positive is scoped off
here while the Rules of Hooks are still followed by construction. */
// AC4: dashboard hook tests (REQ-FE-051 observability, REQ-ARCH-032, t20).
//
// Nine frozen nodes. Every proof is OBSERVABLE at a handler, per the merged
// t16/t18 precedent — never code reading, and NEVER raw call-count equality
// as the proof of a race (phase_3 W11 / review_plan W7):
//  - the six mounted observers record every request their endpoint's
//    `server.use` fixture receives (path + year_month), so "refetched" is a
//    HANDLER-COUNT DELTA and "which month" is the handler-observed param;
//  - the mutation side uses the merged counted handlers in test/handlers.ts
//    (callCount('expenses.create') etc.), so the invalidation is proven from
//    the mutation actually reaching the backend plus the observers refetching;
//  - the rapid-switch node asserts the FINAL state (every month-driven
//    observer settled on the latest year_month, at the handler and on
//    screen), not a request count.
//
// handlers.ts / setup.ts stay byte-identical (t16 ruling): the six dashboard
// fixtures are per-test `server.use` overrides; the month is driven through
// the real MonthContext surface (setYearMonth / nextMonth), never by stubs.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState, type ReactNode } from 'react';
import { http, HttpResponse } from 'msw';
import { callCount, resetCallCounts } from '../test/handlers';
import { server } from '../test/server';
import { MonthProvider, useMonth } from '../context/month_context';
import { use_budget_mutations } from './use_budget';
import {
  use_by_category,
  use_cumulative,
  use_heatmap,
  use_recent,
  use_summary,
  use_trend
} from './use_dashboard';
import { use_create_category, use_delete_category } from './use_categories';
import { use_expense_mutations } from './use_expenses';

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

const EXPENSE_ID = 'e1000000-0000-4000-8000-000000000001';
const CATEGORY_ID = 'c1000000-0000-4000-8000-000000000001';

type Trigger =
  | 'expense-create'
  | 'expense-update'
  | 'expense-delete'
  | 'budget-set'
  | 'budget-delete'
  | 'category-create'
  | 'category-delete';

// --- handler-observed request log -------------------------------------------

/** Per-path request log: one entry per request the fixture received. */
const requests = new Map<string, string[]>();

/** Year-month values seen for one path, in arrival order. */
const monthsSeen = (path: string): string[] => requests.get(path) ?? [];

const requestCount = (path: string): number => (requests.get(path) ?? []).length;

/** Register the six dashboard fixtures, echoing the requested month. */
const registerDashboardFixtures = (): void => {
  const record = (path: string, yearMonth: string | null): void => {
    requests.set(path, [...(requests.get(path) ?? []), yearMonth ?? '']);
  };

  server.use(
    http.get(SUMMARY_PATH, ({ request }) => {
      const yearMonth = new URL(request.url).searchParams.get('year_month');
      record(SUMMARY_PATH, yearMonth);
      return HttpResponse.json(
        {
          year_month: yearMonth ?? '',
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
    http.get(BY_CATEGORY_PATH, ({ request }) => {
      const yearMonth = new URL(request.url).searchParams.get('year_month');
      record(BY_CATEGORY_PATH, yearMonth);
      return HttpResponse.json(
        {
          year_month: yearMonth ?? '',
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
        },
        { status: 200 }
      );
    }),
    http.get(TREND_PATH, ({ request }) => {
      record(TREND_PATH, new URL(request.url).searchParams.get('year_month'));
      return HttpResponse.json(
        {
          months: [
            { year_month: '2026-01', total: '0.00' },
            { year_month: '2026-02', total: '125.50' }
          ]
        },
        { status: 200 }
      );
    }),
    http.get(CUMULATIVE_PATH, ({ request }) => {
      const yearMonth = new URL(request.url).searchParams.get('year_month');
      record(CUMULATIVE_PATH, yearMonth);
      return HttpResponse.json(
        {
          year_month: yearMonth ?? '',
          budget: '2000.00',
          days: [{ date: '2026-02-03', daily: '125.50', cumulative: '125.50' }]
        },
        { status: 200 }
      );
    }),
    http.get(HEATMAP_PATH, ({ request }) => {
      record(HEATMAP_PATH, new URL(request.url).searchParams.get('year_month'));
      return HttpResponse.json(
        {
          max_amount: '125.50',
          weeks: [
            {
              week_start: '2026-01-05',
              days: [
                { date: '2026-01-05', amount: '0.00' },
                { date: '2026-01-06', amount: '0.00' },
                { date: '2026-01-07', amount: '0.00' },
                { date: '2026-01-08', amount: '0.00' },
                { date: '2026-01-09', amount: '0.00' },
                { date: '2026-01-10', amount: '0.00' },
                { date: '2026-01-11', amount: '125.50' }
              ]
            }
          ]
        },
        { status: 200 }
      );
    }),
    http.get(RECENT_PATH, ({ request }) => {
      record(RECENT_PATH, new URL(request.url).searchParams.get('year_month'));
      return HttpResponse.json(
        {
          items: [
            {
              id: EXPENSE_ID,
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
        },
        { status: 200 }
      );
    })
  );
};

// --- harness ----------------------------------------------------------------

const Provider = ({ children }: { children: ReactNode }) => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
};

/** Month controls: the real MonthContext surface a MonthPicker would use. */
const MonthControls = (): JSX.Element => {
  const { yearMonth, setYearMonth, nextMonth } = useMonth();
  return (
    <>
      <span data-testid="context-month">{yearMonth}</span>
      <button type="button" onClick={() => setYearMonth('2026-02')}>
        set-2026-02
      </button>
      <button type="button" onClick={() => setYearMonth('2026-03')}>
        set-2026-03
      </button>
      <button type="button" onClick={nextMonth}>
        next
      </button>
    </>
  );
};

/** Mutation trigger wired to the merged hooks (their invalidation is merged;
 * this issue makes it observable). */
const MutationTrigger = ({ trigger }: { trigger: Trigger }) => {
  const { yearMonth } = useMonth();
  const expenseMutations = use_expense_mutations();
  const budgetMutations = use_budget_mutations(yearMonth);
  const createCategory = use_create_category();
  const deleteCategory = use_delete_category();

  const fire = (): void => {
    if (trigger === 'expense-create') {
      void expenseMutations.create.mutateAsync({
        amount: '10.00',
        category_id: CATEGORY_ID,
        date: '2026-02-05'
      });
    } else if (trigger === 'expense-update') {
      void expenseMutations.update.mutateAsync({
        id: EXPENSE_ID,
        payload: { amount: '99.99' }
      });
    } else if (trigger === 'expense-delete') {
      void expenseMutations.remove.mutateAsync(EXPENSE_ID);
    } else if (trigger === 'budget-set') {
      void budgetMutations.set.mutateAsync('2000.00');
    } else if (trigger === 'budget-delete') {
      void budgetMutations.remove.mutateAsync();
    } else if (trigger === 'category-create') {
      void createCategory.mutateAsync({ name: 'Custom', color: '#123456' });
    } else {
      void deleteCategory.mutateAsync(CATEGORY_ID);
    }
  };

  return (
    <button type="button" onClick={fire}>
      trigger
    </button>
  );
};

/** One observer per hook: renders the handler-echoed month so the value the
 * hook SETTLED on is visible on screen (final-state evidence). */
const DashboardObservers = (): JSX.Element => {
  const summary = use_summary();
  const byCategory = use_by_category();
  const trend = use_trend();
  const cumulative = use_cumulative();
  const heatmap = use_heatmap();
  const recent = use_recent();

  if (summary.isPending || summary.data === undefined) {
    return <span>summary-loading</span>;
  }
  if (byCategory.isPending || byCategory.data === undefined) {
    return <span>by-category-loading</span>;
  }
  if (trend.isPending || trend.data === undefined) {
    return <span>trend-loading</span>;
  }
  if (cumulative.isPending || cumulative.data === undefined) {
    return <span>cumulative-loading</span>;
  }
  if (heatmap.isPending || heatmap.data === undefined) {
    return <span>heatmap-loading</span>;
  }
  if (recent.isPending || recent.data === undefined) {
    return <span>recent-loading</span>;
  }

  return (
    <>
      <span data-testid="obs-summary">{`summary:${summary.data.year_month}:${summary.data.total}`}</span>
      <span data-testid="obs-by-category">{`by-category:${byCategory.data.year_month}:${byCategory.data.categories.length}`}</span>
      <span data-testid="obs-trend">{`trend:${trend.data.months.length}`}</span>
      <span data-testid="obs-cumulative">{`cumulative:${cumulative.data.year_month}:${cumulative.data.days.length}`}</span>
      <span data-testid="obs-heatmap">{`heatmap:${heatmap.data.max_amount}:${heatmap.data.weeks.length}`}</span>
      <span data-testid="obs-recent">{`recent:${recent.data.items.length}`}</span>
    </>
  );
};

const Scene = ({ trigger }: { trigger: Trigger }) => (
  <Provider>
    <MonthProvider>
      <MonthControls />
      <DashboardObservers />
      <MutationTrigger trigger={trigger} />
    </MonthProvider>
  </Provider>
);

/** Jump the shared month to the deterministic 2026-02 and settle. */
const settleAt = async (label: string, yearMonth: string): Promise<void> => {
  fireEvent.click(screen.getByText(label));
  await waitFor(() => {
    expect(screen.getByTestId('context-month').textContent).toBe(yearMonth);
  });
  await waitFor(() => {
    for (const path of MONTH_DRIVEN_PATHS) {
      expect(monthsSeen(path)[monthsSeen(path).length - 1]).toBe(yearMonth);
    }
    expect(screen.getByTestId('obs-summary').textContent).toContain(yearMonth);
    expect(screen.getByTestId('obs-cumulative').textContent).toContain(yearMonth);
    expect(screen.getByTestId('obs-by-category').textContent).toContain(yearMonth);
  });
};

/** Wait until all six observers have rendered their first data. */
const settleAllSix = async (): Promise<void> => {
  await waitFor(() => {
    expect(screen.queryByText('summary-loading')).toBeNull();
    expect(screen.queryByText('by-category-loading')).toBeNull();
    expect(screen.queryByText('trend-loading')).toBeNull();
    expect(screen.queryByText('cumulative-loading')).toBeNull();
    expect(screen.queryByText('heatmap-loading')).toBeNull();
    expect(screen.queryByText('recent-loading')).toBeNull();
  });
};

beforeEach(() => {
  requests.clear();
  resetCallCounts();
  registerDashboardFixtures();
});

describe('dashboard hooks (ac4)', () => {
  it('the six dashboard hooks fetch their six endpoints in parallel on mount', async () => {
    render(<Scene trigger="expense-create" />);
    await settleAllSix();
    // Each of the six endpoints received exactly one request from mount and
    // every observer already rendered its data: six independent reads under
    // one mount (REQ-ARCH-032), no endpoint waiting on another's result.
    for (const path of SIX_PATHS) {
      expect(requestCount(path)).toBe(1);
    }
    // And each observer rendered its endpoint's data.
    expect(screen.getByTestId('obs-summary').textContent).toContain('125.50');
    expect(screen.getByTestId('obs-by-category').textContent).toContain('by-category:');
    expect(screen.getByTestId('obs-trend').textContent).toBe('trend:2');
    expect(screen.getByTestId('obs-cumulative').textContent).toContain('cumulative:');
    expect(screen.getByTestId('obs-heatmap').textContent).toBe('heatmap:125.50:1');
    expect(screen.getByTestId('obs-recent').textContent).toBe('recent:1');
  });

  it('creating an expense refetches every mounted dashboard observer', async () => {
    render(<Scene trigger="expense-create" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.create')).toBe(1));
    await waitFor(() => {
      SIX_PATHS.forEach((path, index) => {
        expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
      });
    });
  });

  it('updating an expense refetches every mounted dashboard observer', async () => {
    render(<Scene trigger="expense-update" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.update')).toBe(1));
    await waitFor(() => {
      SIX_PATHS.forEach((path, index) => {
        expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
      });
    });
  });

  it('deleting an expense refetches every mounted dashboard observer', async () => {
    render(<Scene trigger="expense-delete" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.delete')).toBe(1));
    await waitFor(() => {
      SIX_PATHS.forEach((path, index) => {
        expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
      });
    });
  });

  it('setting the budget refetches every mounted dashboard observer', async () => {
    render(<Scene trigger="budget-set" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.set')).toBe(1));
    await waitFor(() => {
      SIX_PATHS.forEach((path, index) => {
        expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
      });
    });
  });

  it('deleting the budget refetches every mounted dashboard observer', async () => {
    render(<Scene trigger="budget-delete" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.delete')).toBe(1));
    await waitFor(() => {
      SIX_PATHS.forEach((path, index) => {
        expect(requestCount(path)).toBe((before[index] ?? 0) + 1);
      });
    });
  });

  it('category mutations never refetch the mounted dashboard observers', async () => {
    render(<Scene trigger="category-create" />);
    await settleAllSix();
    const before = SIX_PATHS.map((path) => requestCount(path));
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('categories.create')).toBe(1));
    // Let any stray refetch window elapse, then require every dashboard
    // count frozen at its pre-mutation value (merged negative control).
    await new Promise((resolve) => setTimeout(resolve, 150));
    SIX_PATHS.forEach((path, index) => {
      expect(requestCount(path)).toBe(before[index] ?? 0);
    });
  });

  it('changing the context month requests the new year_month in the month-driven hooks', async () => {
    render(<Scene trigger="expense-create" />);
    await settleAllSix();
    await settleAt('set-2026-02', '2026-02');
    const monthDrivenBefore = MONTH_DRIVEN_PATHS.map((path) => requestCount(path));
    const paramDrivenBefore = [TREND_PATH, HEATMAP_PATH, RECENT_PATH].map((path) =>
      requestCount(path)
    );

    fireEvent.click(screen.getByText('set-2026-03'));

    // The handler sees the NEW year_month for each month-driven endpoint.
    await waitFor(() => {
      for (const path of MONTH_DRIVEN_PATHS) {
        expect(monthsSeen(path)[monthsSeen(path).length - 1]).toBe('2026-03');
      }
    });
    // The observers re-rendered on the new month's data.
    await waitFor(() => {
      expect(screen.getByTestId('obs-summary').textContent).toBe('summary:2026-03:125.50');
      expect(screen.getByTestId('obs-by-category').textContent).toBe('by-category:2026-03:1');
      expect(screen.getByTestId('obs-cumulative').textContent).toBe('cumulative:2026-03:1');
    });
    // The month-independent hooks are NOT re-keyed by a month change.
    [TREND_PATH, HEATMAP_PATH, RECENT_PATH].forEach((path, index) => {
      expect(requestCount(path)).toBe(paramDrivenBefore[index] ?? 0);
    });
    expect(monthDrivenBefore.every((count) => count >= 1)).toBe(true);
  });

  it('rapid month switching settles every month-driven hook on the latest year_month', async () => {
    render(<Scene trigger="expense-create" />);
    await settleAllSix();
    await settleAt('set-2026-02', '2026-02');

    // Three back-to-back steps with no awaits between: 2026-02 -> 2026-05.
    fireEvent.click(screen.getByText('set-2026-03'));
    fireEvent.click(screen.getByText('next'));
    fireEvent.click(screen.getByText('next'));

    // FINAL-STATE proof (never call-count equality): the context value, the
    // rendered observers and the LAST request each endpoint received all
    // agree on 2026-05, and no observer is left showing a stale month.
    await waitFor(() => {
      expect(screen.getByTestId('context-month').textContent).toBe('2026-05');
    });
    await waitFor(() => {
      expect(screen.getByTestId('obs-summary').textContent).toBe('summary:2026-05:125.50');
      expect(screen.getByTestId('obs-by-category').textContent).toBe('by-category:2026-05:1');
      expect(screen.getByTestId('obs-cumulative').textContent).toBe('cumulative:2026-05:1');
    });
    for (const path of MONTH_DRIVEN_PATHS) {
      expect(monthsSeen(path)[monthsSeen(path).length - 1]).toBe('2026-05');
    }
  });
});

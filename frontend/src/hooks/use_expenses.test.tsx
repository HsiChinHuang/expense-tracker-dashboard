// AC3: expense hook + invalidation-matrix tests (REQ-FE-051).
//
// The invalidation proof is MSW handler CALL COUNTS on mounted observers:
// each mutation test mounts the real expense list observer AND a dummy
// observer keyed exactly ["dashboard","probe"] whose queryFn hits the
// counted probe handler in src/test/handlers.ts. Assertions compare
// handler counts before/after the mutation (refetch = count delta) —
// never code reading.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { api } from '../api/client';
import { DASHBOARD_PROBE_PATH, callCount, resetCallCounts } from '../test/handlers';
import { use_expense_detail, use_expenses, use_expense_mutations } from './use_expenses';

const DASHBOARD_KEY = ['dashboard', 'probe'] as const;
const EXPENSE_ID = 'e1000000-0000-4000-8000-000000000001';
const CATEGORY_ID = 'c1000000-0000-4000-8000-000000000001';

type Trigger = 'create' | 'update' | 'delete';

/** Probe queryFn: goes through the shared client to the counted handler. */
const probeFn = async (): Promise<{ ok: boolean }> => {
  const response = await api.get<{ ok: boolean }>(DASHBOARD_PROBE_PATH);
  return response.data;
};

const Provider = ({ children }: { children: ReactNode }) => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
};

/** Dummy observer mounted on the exact ["dashboard","probe"] key. */
const DashboardObserver = () => {
  const query = useQuery({ queryKey: DASHBOARD_KEY, queryFn: probeFn });
  if (query.isPending) {
    return <span>probe-loading</span>;
  }
  return <span>probe-ok</span>;
};

/** List observer + mutation trigger button. */
const ExpenseHarness = ({ trigger }: { trigger: Trigger }) => {
  const list = use_expenses({ page: 1, page_size: 20 });
  const mutations = use_expense_mutations();
  const fire = (): void => {
    if (trigger === 'create') {
      void mutations.create.mutateAsync({
        amount: '10.00',
        category_id: CATEGORY_ID,
        date: '2026-02-05'
      });
    } else if (trigger === 'update') {
      void mutations.update.mutateAsync({
        id: EXPENSE_ID,
        payload: { amount: '99.99' }
      });
    } else {
      void mutations.remove.mutateAsync(EXPENSE_ID);
    }
  };
  if (list.isPending) {
    return <span>loading</span>;
  }
  return (
    <button type="button" onClick={fire}>
      trigger
    </button>
  );
};

const MutationScene = ({ trigger }: { trigger: Trigger }) => (
  <Provider>
    <ExpenseHarness trigger={trigger} />
    <DashboardObserver />
  </Provider>
);

/** Wait until both mounted observers have completed their first fetch. */
const settleObservers = async (): Promise<void> => {
  await waitFor(() => {
    expect(callCount('expenses.list')).toBe(1);
    expect(callCount('dashboard.probe')).toBe(1);
  });
};

beforeEach(() => {
  resetCallCounts();
});

describe('expense hooks', () => {
  it('use_expenses renders the paginated envelope fetched through the api module', async () => {
    const view = render(
      <Provider>
        <StaticListHarness />
      </Provider>
    );
    await waitFor(() => expect(screen.queryByText('loading')).toBeNull());
    expect(view.getByText(/total:1/)).toBeTruthy();
    expect(view.getByText(/item:125\.50/)).toBeTruthy();
    // Fetched exactly once through the api module -> counted handler.
    expect(callCount('expenses.list')).toBe(1);
  });

  it('use_expense_detail fetches one expense by id', async () => {
    render(
      <Provider>
        <DetailHarness id={EXPENSE_ID} />
      </Provider>
    );
    await waitFor(() => expect(screen.queryByText('loading')).toBeNull());
    expect(screen.getByText(`detail:${EXPENSE_ID}`)).toBeTruthy();
    expect(callCount('expenses.detail')).toBe(1);
  });

  it('creating an expense refetches the mounted expenses list observer', async () => {
    render(<MutationScene trigger="create" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.create')).toBe(1));
    await waitFor(() => expect(callCount('expenses.list')).toBe(2));
  });

  it('creating an expense refetches the mounted dashboard-prefixed observer', async () => {
    render(<MutationScene trigger="create" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.create')).toBe(1));
    await waitFor(() => expect(callCount('dashboard.probe')).toBe(2));
  });

  it('updating an expense refetches the expenses list and dashboard observers', async () => {
    render(<MutationScene trigger="update" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.update')).toBe(1));
    await waitFor(() => {
      expect(callCount('expenses.list')).toBe(2);
      expect(callCount('dashboard.probe')).toBe(2);
    });
  });

  it('deleting an expense refetches the expenses list and dashboard observers', async () => {
    render(<MutationScene trigger="delete" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.delete')).toBe(1));
    await waitFor(() => {
      expect(callCount('expenses.list')).toBe(2);
      expect(callCount('dashboard.probe')).toBe(2);
    });
  });

  it('expense mutations never call the categories or budgets handlers', async () => {
    render(<MutationScene trigger="delete" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('expenses.delete')).toBe(1));
    await waitFor(() => expect(callCount('expenses.list')).toBe(2));
    expect(callCount('categories.list')).toBe(0);
    expect(callCount('categories.create')).toBe(0);
    expect(callCount('categories.delete')).toBe(0);
    expect(callCount('budgets.get')).toBe(0);
    expect(callCount('budgets.set')).toBe(0);
    expect(callCount('budgets.delete')).toBe(0);
  });
});

// Static list-only harness (no mutation) for the render test.
function StaticListHarness() {
  const list = use_expenses();
  if (list.isPending || list.data === undefined) {
    return <span>loading</span>;
  }
  const first = list.data.items[0];
  return <span>{`total:${list.data.total} item:${first ? first.amount : '-'}`}</span>;
}

function DetailHarness({ id }: { id: string }) {
  const detail = use_expense_detail(id);
  if (detail.isPending || detail.data === undefined) {
    return <span>loading</span>;
  }
  return <span>{`detail:${detail.data.id}`}</span>;
}

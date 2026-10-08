// AC3: budget hook + invalidation-matrix tests (REQ-FE-051).
//
// Same MSW call-count mechanism as use_expenses.test.tsx: a mounted
// ["budgets","month",ym] observer plus the dummy ["dashboard","probe"]
// observer; mutations are fired from a button and the proof is handler
// count deltas. The absent-month node also pins that "0.00" survives as a
// STRING (no number coercion anywhere in the api/hook layer).

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { api } from '../api/client';
import { queryKeys } from '../api/query_keys';
import { DASHBOARD_PROBE_PATH, callCount, resetCallCounts } from '../test/handlers';
import { use_budget, use_budget_mutations } from './use_budget';

const DASHBOARD_KEY = ['dashboard', 'probe'] as const;
const MONTH = '2026-02';
const ABSENT_MONTH = '2020-01';

type Trigger = 'set' | 'delete';

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

const DashboardObserver = () => {
  const query = useQuery({ queryKey: DASHBOARD_KEY, queryFn: probeFn });
  return <span>{query.isPending ? 'probe-loading' : 'probe-ok'}</span>;
};

/** Month observer + mutation trigger button. */
const BudgetHarness = ({ trigger, month }: { trigger: Trigger; month: string }) => {
  const budget = use_budget(month);
  const mutations = use_budget_mutations(month);
  const fire = (): void => {
    if (trigger === 'set') {
      void mutations.set.mutateAsync('2500.00');
    } else {
      void mutations.remove.mutateAsync();
    }
  };
  if (budget.isPending) {
    return <span>loading</span>;
  }
  return (
    <button type="button" onClick={fire}>
      trigger
    </button>
  );
};

/** Read-only harness that renders the resolved amount verbatim. */
const BudgetTextHarness = ({ month }: { month: string }) => {
  const budget = use_budget(month);
  if (budget.isPending || budget.data === undefined) {
    return <span>loading</span>;
  }
  return (
    <span>
      {`ym:${budget.data.year_month} amount:${budget.data.amount} typeof:${typeof budget.data.amount}`}
    </span>
  );
};

const MutationScene = ({ trigger }: { trigger: Trigger }) => (
  <Provider>
    <BudgetHarness trigger={trigger} month={MONTH} />
    <DashboardObserver />
  </Provider>
);

const settleObservers = async (): Promise<void> => {
  await waitFor(() => {
    expect(callCount('budgets.get')).toBe(1);
    expect(callCount('dashboard.probe')).toBe(1);
  });
};

beforeEach(() => {
  resetCallCounts();
});

describe('budget hooks', () => {
  it('use_budget resolves the absent month to the string 0.00 without number coercion', async () => {
    render(
      <Provider>
        <BudgetTextHarness month={ABSENT_MONTH} />
      </Provider>
    );
    await waitFor(() => expect(screen.queryByText('loading')).toBeNull());
    // The 2-dp string survives end to end: rendered verbatim, typeof string.
    expect(screen.getByText(`ym:${ABSENT_MONTH} amount:0.00 typeof:string`)).toBeTruthy();
    expect(callCount('budgets.get')).toBe(1);
  });

  it('setting a budget refetches the mounted budgets month observer', async () => {
    render(<MutationScene trigger="set" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.set')).toBe(1));
    await waitFor(() => expect(callCount('budgets.get')).toBe(2));
  });

  it('setting a budget refetches the mounted dashboard-prefixed observer', async () => {
    render(<MutationScene trigger="set" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.set')).toBe(1));
    await waitFor(() => expect(callCount('dashboard.probe')).toBe(2));
  });

  it('deleting a budget invalidates the budgets key and refetches the month observer', async () => {
    render(<MutationScene trigger="delete" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.delete')).toBe(1));
    await waitFor(() => expect(callCount('budgets.get')).toBe(2));
    // The invalidated key is the factory key for this month.
    expect(queryKeys.budgets.byMonth(MONTH)).toEqual(['budgets', 'month', MONTH]);
  });

  it('budget mutations never call the expenses or categories handlers', async () => {
    render(<MutationScene trigger="set" />);
    await settleObservers();
    fireEvent.click(screen.getByText('trigger'));
    await waitFor(() => expect(callCount('budgets.set')).toBe(1));
    await waitFor(() => expect(callCount('budgets.get')).toBe(2));
    expect(callCount('expenses.list')).toBe(0);
    expect(callCount('expenses.create')).toBe(0);
    expect(callCount('expenses.detail')).toBe(0);
    expect(callCount('expenses.update')).toBe(0);
    expect(callCount('expenses.delete')).toBe(0);
    expect(callCount('categories.list')).toBe(0);
    expect(callCount('categories.create')).toBe(0);
    expect(callCount('categories.delete')).toBe(0);
  });
});

// AC3: category hook + invalidation tests (REQ-FE-051).
//
// Same MSW call-count mechanism. Categories carry the REQ-FE-051
// asymmetry: create/delete invalidate ["categories"] ONLY, so the mounted
// ["dashboard","probe"] observer must NOT refetch (negative control).

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { api } from '../api/client';
import { DASHBOARD_PROBE_PATH, callCount, resetCallCounts } from '../test/handlers';
import {
  use_categories,
  use_create_category,
  use_delete_category
} from './use_categories';

const DASHBOARD_KEY = ['dashboard', 'probe'] as const;
const CATEGORY_ID = 'c1000000-0000-4000-8000-000000000001';

type Trigger = 'create' | 'delete';

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

/** Categories observer + mutation trigger button. */
const CategoryHarness = ({ trigger }: { trigger: Trigger }) => {
  const list = use_categories();
  const create = use_create_category();
  const remove = use_delete_category();
  const fire = (): void => {
    if (trigger === 'create') {
      void create.mutateAsync({ name: 'Custom', color: '#123456', icon: 'star' });
    } else {
      void remove.mutateAsync(CATEGORY_ID);
    }
  };
  if (list.isPending || list.data === undefined) {
    return <span>loading</span>;
  }
  const first = list.data.categories[0];
  return (
    <button type="button" onClick={fire}>
      {`trigger:${first ? first.name : '-'}:${list.data.categories.length}`}
    </button>
  );
};

const MutationScene = ({ trigger }: { trigger: Trigger }) => (
  <Provider>
    <CategoryHarness trigger={trigger} />
    <DashboardObserver />
  </Provider>
);

const settleObservers = async (): Promise<void> => {
  await waitFor(() => {
    expect(callCount('categories.list')).toBe(1);
    expect(callCount('dashboard.probe')).toBe(1);
  });
};

beforeEach(() => {
  resetCallCounts();
});

describe('category hooks', () => {
  it('use_categories renders the category list fetched through the api module', async () => {
    render(
      <Provider>
        <CategoryHarness trigger="create" />
      </Provider>
    );
    await waitFor(() => expect(screen.queryByText('loading')).toBeNull());
    // The object-wrapper body unwraps to the one fixture category.
    expect(screen.getByText('trigger:Food:1')).toBeTruthy();
    expect(callCount('categories.list')).toBe(1);
  });

  it('creating a category refetches the mounted categories observer', async () => {
    render(<MutationScene trigger="create" />);
    await settleObservers();
    fireEvent.click(screen.getByText(/trigger:/));
    await waitFor(() => expect(callCount('categories.create')).toBe(1));
    await waitFor(() => expect(callCount('categories.list')).toBe(2));
  });

  it('deleting a category refetches the mounted categories observer', async () => {
    render(<MutationScene trigger="delete" />);
    await settleObservers();
    fireEvent.click(screen.getByText(/trigger:/));
    await waitFor(() => expect(callCount('categories.delete')).toBe(1));
    await waitFor(() => expect(callCount('categories.list')).toBe(2));
  });

  it('category mutations never call the expenses or budgets handlers', async () => {
    render(<MutationScene trigger="create" />);
    await settleObservers();
    fireEvent.click(screen.getByText(/trigger:/));
    await waitFor(() => expect(callCount('categories.create')).toBe(1));
    await waitFor(() => expect(callCount('categories.list')).toBe(2));
    expect(callCount('expenses.list')).toBe(0);
    expect(callCount('expenses.create')).toBe(0);
    expect(callCount('expenses.detail')).toBe(0);
    expect(callCount('expenses.update')).toBe(0);
    expect(callCount('expenses.delete')).toBe(0);
    expect(callCount('budgets.get')).toBe(0);
    expect(callCount('budgets.set')).toBe(0);
    expect(callCount('budgets.delete')).toBe(0);
  });

  it('category mutations do not refetch the dashboard-prefixed observer', async () => {
    render(<MutationScene trigger="delete" />);
    await settleObservers();
    fireEvent.click(screen.getByText(/trigger:/));
    await waitFor(() => expect(callCount('categories.delete')).toBe(1));
    // The categories invalidation must NOT touch the ["dashboard"] prefix:
    // let any stray refetch window elapse, then require the count frozen.
    await waitFor(() => expect(callCount('categories.list')).toBe(2));
    await new Promise((resolve) => setTimeout(resolve, 150));
    expect(callCount('dashboard.probe')).toBe(1);
  });
});

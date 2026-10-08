// AC1/AC2/AC4: ExpensesPage (REQ-FE-063, REQ-FE-100/101/102, REQ-FE-015,
// REQ-PROD-023/036, REQ-FE-103 — t17). Frozen titles (13 nodes): the two
// network-error nodes grepped by ac1, nine table/filter/pagination/state
// nodes by ac2, the two confirm-dialog nodes by ac4.
//
// Proof mechanisms are OBSERVABLE, per the groom audit:
// - retry: server.use override on /api/v1/expenses fails FIRST (the merged
//   t9 interceptor normalizes HttpResponse.error() to NETWORK_ERROR), then
//   serves the envelope; the retry click flips the table to loaded.
// - filters/pagination: query params asserted AT THE HANDLER (t9 precedent).
// - confirm dialog: merged t16 callCount deltas from src/test/handlers.ts.
// Mounts carry their own QueryClient (retry:false, staleTime:0) per the
// issue STATE/QUERY RULES; handlers.ts / setup.ts are untouched.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { server } from '../test/server';
import { ToastProvider } from '../context/toast_context';
import { ExpensesPage } from './expenses_page';
import { demoCategory, demoExpense, callCount, resetCallCounts } from '../test/handlers';
import type { Expense, ExpenseList } from '../api/expenses';

/** Second-row fixture with the frozen 500-character note (ac2 long note). */
const longNote = 'x'.repeat(500);
const longNoteExpense: Expense = {
  ...demoExpense,
  id: 'e3000000-0000-4000-8000-000000000003',
  amount: '0.01',
  note: longNote
};

const envelope = (items: Expense[], page: number, pageSize: number, total: number): ExpenseList => ({
  items,
  total,
  page,
  page_size: pageSize
});

const renderPage = (): void => {
  render(
    <ToastProvider>
      <PageProviders>
        <ExpensesPage />
      </PageProviders>
    </ToastProvider>
  );
};

/** Per-mount QueryClient with the pinned options (STATE/QUERY RULES). */
const PageProviders = ({ children }: { children: ReactNode }): JSX.Element => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
};

/** Wait until the default list query has served its first response. */
const tableLoaded = async (): Promise<void> => {
  await waitFor(() => {
    expect(screen.queryByText('groceries')).not.toBeNull();
  });
};

beforeEach(() => {
  resetCallCounts();
});

describe('ExpensesPage network error (ac1)', () => {
  it('a failed list query renders the offline error state with a retry button', async () => {
    let attempts = 0;
    server.use(
      http.get('/api/v1/expenses', () => {
        attempts += 1;
        if (attempts === 1) {
          // Merged t9 interceptor normalizes this to NETWORK_ERROR.
          return HttpResponse.error();
        }
        return HttpResponse.json(envelope([demoExpense], 1, 20, 1), { status: 200 });
      })
    );
    renderPage();
    await waitFor(() => {
      const alert = screen.getByRole('alert');
      expect(alert.textContent).toContain('Could not load expenses');
    });
    expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
    // The table never rendered from the failed query.
    expect(screen.queryByText('groceries')).toBeNull();
    expect(attempts).toBe(1);
  });

  it('retrying the failed list query refetches through the handler and renders the table', async () => {
    let attempts = 0;
    server.use(
      http.get('/api/v1/expenses', () => {
        attempts += 1;
        if (attempts === 1) {
          return HttpResponse.error();
        }
        return HttpResponse.json(envelope([demoExpense], 1, 20, 1), { status: 200 });
      })
    );
    renderPage();
    const retry = await screen.findByRole('button', { name: 'Retry' });
    expect(attempts).toBe(1);
    fireEvent.click(retry);
    await tableLoaded();
    // The retry click RE-INVOKED the query: second hit at the handler.
    expect(attempts).toBe(2);
    expect(screen.queryByRole('alert')).toBeNull();
    expect(screen.getByText(demoExpense.amount)).toBeTruthy();
  });
});

describe('ExpensesPage table, filters, pagination (ac2)', () => {
  it('the page sets the Expenses document title per the page title pattern', async () => {
    renderPage();
    await tableLoaded();
    expect(document.title).toBe('Expenses');
  });

  it('a pending list query renders the loading status region', () => {
    renderPage();
    // Synchronously (before the handler resolves) the role=status region is up.
    const status = screen.getByRole('status');
    expect(status.textContent).toContain('Loading expenses');
  });

  it('an empty result renders the empty state message', async () => {
    server.use(
      http.get('/api/v1/expenses', () =>
        HttpResponse.json(envelope([], 1, 20, 0), { status: 200 })
      )
    );
    renderPage();
    expect(await screen.findByText('No expenses yet. Add your first expense.')).toBeTruthy();
    expect(screen.queryByRole('status')).toBeNull();
  });

  it('the expenses table renders date category amount note and actions columns', async () => {
    renderPage();
    await tableLoaded();
    const columnHeaders = screen.getAllByRole('columnheader').map((header) => header.textContent);
    expect(columnHeaders).toEqual(['Date', 'Category', 'Amount', 'Note', 'Actions']);
    // The row renders the fixture values through the columns.
    expect(screen.getByText(demoExpense.date)).toBeTruthy();
    // The category name renders in a table cell (it also appears as the
    // filter's selected option label, so assert the TD occurrence).
    expect(screen.getAllByText(demoCategory.name).some((node) => node.tagName === 'TD')).toBe(true);
    expect(screen.getByText('groceries')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Edit' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Delete' })).toBeTruthy();
  });

  it('the amount cell renders the two-decimal string exactly as the api returned it', async () => {
    renderPage();
    await tableLoaded();
    const cell = screen.getByText(demoExpense.amount);
    // Verbatim string, two decimals, untouched by any coercion.
    expect(cell.textContent).toBe('125.50');
    expect(cell.tagName).toBe('TD');
  });

  it('the month filter drives the year_month query param', async () => {
    const seen: string[] = [];
    server.use(
      http.get('/api/v1/expenses', ({ request }) => {
        const url = new URL(request.url);
        seen.push(url.searchParams.get('year_month') ?? '');
        return HttpResponse.json(envelope([demoExpense], 1, 20, 1), { status: 200 });
      })
    );
    renderPage();
    await tableLoaded();
    expect(seen[0]).toBe('');
    fireEvent.change(screen.getByLabelText('Month filter'), {
      target: { value: '2026-02' }
    });
    await waitFor(() => {
      expect(seen).toContain('2026-02');
    });
  });

  it('the category filter drives the category_id query param', async () => {
    const seen: string[] = [];
    server.use(
      http.get('/api/v1/expenses', ({ request }) => {
        const url = new URL(request.url);
        seen.push(url.searchParams.get('category_id') ?? '');
        return HttpResponse.json(envelope([demoExpense], 1, 20, 1), { status: 200 });
      })
    );
    renderPage();
    await tableLoaded();
    expect(seen[0]).toBe('');
    fireEvent.change(screen.getByLabelText('Category filter'), {
      target: { value: demoCategory.id }
    });
    await waitFor(() => {
      expect(seen).toContain(demoCategory.id);
    });
  });

  it('the next page control requests page two with the default page size', async () => {
    const urls: string[] = [];
    server.use(
      http.get('/api/v1/expenses', ({ request }) => {
        urls.push(new URL(request.url).search);
        return HttpResponse.json(envelope([demoExpense], 2, 20, 21), { status: 200 });
      })
    );
    renderPage();
    await tableLoaded();
    fireEvent.click(screen.getByRole('button', { name: 'Next page' }));
    await waitFor(() => {
      expect(screen.getByText('Page 2')).toBeTruthy();
    });
    const second = urls[urls.length - 1] ?? '';
    expect(second).toContain('page=2');
    expect(second).toContain('page_size=20');
  });

  it('a five hundred character note renders in full without truncation', async () => {
    server.use(
      http.get('/api/v1/expenses', () =>
        HttpResponse.json(envelope([longNoteExpense], 1, 20, 1), { status: 200 })
      )
    );
    renderPage();
    const cell = await screen.findByText(longNote);
    expect(cell.textContent).toHaveLength(500);
    expect(cell.textContent).toBe(longNote);
  });
});

describe('ExpensesPage delete confirm (ac4)', () => {
  it('clicking delete opens the confirm dialog without calling the delete handler', async () => {
    renderPage();
    await tableLoaded();
    const before = callCount('expenses.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    const dialog = await screen.findByRole('dialog', { name: 'Delete expense' });
    expect(dialog).toBeTruthy();
    // No DELETE request left the page while the dialog is open.
    expect(callCount('expenses.delete')).toBe(before);
    expect(callCount('expenses.delete')).toBe(0);
  });

  it('confirming the delete calls the delete handler and refetches the list', async () => {
    renderPage();
    await tableLoaded();
    const listBefore = callCount('expenses.list');
    const deleteBefore = callCount('expenses.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Confirm' }));
    // Handler actually invoked (count delta, not code reading).
    await waitFor(() => {
      expect(callCount('expenses.delete')).toBe(deleteBefore + 1);
    });
    // REQ-FE-051: the mutation invalidates ["expenses"] -> mounted list refetches.
    await waitFor(() => {
      expect(callCount('expenses.list')).toBeGreaterThan(listBefore);
    });
    // Toast-on-success half of REQ-FE-081.
    expect(await screen.findByText('Expense deleted')).toBeTruthy();
  });
});

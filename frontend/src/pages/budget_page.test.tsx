// AC1/AC2: BudgetPage (REQ-FE-064, REQ-PROD-012, REQ-FE-100/101/102/103,
// REQ-FE-015 — t18). Frozen titles (14 nodes): ten display/picker/delete
// nodes grepped by ac1, four history/helper nodes by ac2.
//
// Proof mechanisms are OBSERVABLE, per the merged t17 precedent:
// - the month picker's effect is asserted AT THE HANDLER (the requested
//   /api/v1/budgets/{year_month} path), not by code reading;
// - the retry node uses a server.use fail-once override (the merged t9
//   interceptor normalizes HttpResponse.error() to NETWORK_ERROR) and the
//   rejection is CONSUMED in-test by the query error state (Q12);
// - the confirm-dialog nodes use merged t16 callCount deltas;
// - the 12-month history is asserted on data-testid="budget-history-row"
//   (Q3): twelve mounted use_budget observers, no useQueries, no endpoint.
// Mounts carry their own QueryClient (retry:false, staleTime:0) per the
// STATE/QUERY RULES; handlers.ts / setup.ts are untouched.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { server } from '../test/server';
import { ToastProvider } from '../context/toast_context';
import { BudgetPage, monthWindow, shiftMonth } from './budget_page';
import { demoBudget, callCount, resetCallCounts } from '../test/handlers';
import type { Budget } from '../api/budgets';

/** Budget payload served for EVERY month (history rows included). */
const anyMonth = (amount: string): Budget => ({
  year_month: demoBudget.year_month,
  amount
});

const renderPage = (): void => {
  render(
    <ToastProvider>
      <PageProviders>
        <BudgetPage />
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

/** Read the month picker's current value (also the mounted query month). */
const pickerValue = (): string =>
  (screen.getByLabelText('Budget month') as HTMLInputElement).value;

/** Wait until the display observer has served its first response. */
const displayLoaded = async (): Promise<void> => {
  await waitFor(() => {
    expect(screen.queryByTestId('budget-amount')).not.toBeNull();
  });
};

beforeEach(() => {
  resetCallCounts();
});

describe('BudgetPage budget display (ac1)', () => {
  it('the page sets the Budget document title', async () => {
    server.use(
      http.get('/api/v1/budgets/:year_month', () => HttpResponse.json(anyMonth('2000.00')))
    );
    renderPage();
    await displayLoaded();
    expect(document.title).toBe('Budget');
  });

  it('a pending budget query renders the loading status region', () => {
    renderPage();
    // Synchronously (before the handler resolves) the role=status region is up.
    const status = screen.getByRole('status');
    expect(status.textContent).toContain('Loading budget');
  });

  it('the budget display renders the amount string exactly as the api returned it', async () => {
    server.use(
      http.get('/api/v1/budgets/:year_month', () => HttpResponse.json(anyMonth('2000.00')))
    );
    renderPage();
    await displayLoaded();
    const cell = screen.getByTestId('budget-amount');
    // Verbatim string, two decimals, untouched by any coercion.
    expect(cell.textContent).toBe('2000.00');
    expect(cell.textContent).toBe(demoBudget.amount);
  });

  it('the absent month renders the no budget yet empty state with no delete control', async () => {
    // The API's absent-month contract: 200 with the string "0.00".
    server.use(
      http.get('/api/v1/budgets/:year_month', ({ request }) =>
        HttpResponse.json({
          year_month: new URL(request.url).pathname.split('/').pop() ?? '',
          amount: '0.00'
        })
      )
    );
    renderPage();
    expect(
      await screen.findByText('No budget yet. Set a budget to start tracking.')
    ).toBeTruthy();
    // Q9: the delete affordance is ABSENT from the DOM, not disabled.
    expect(screen.queryByRole('button', { name: /delete/i })).toBeNull();
  });

  it('a failed budget query renders the offline error state with a retry button', async () => {
    const failedMonth = pickerValueAtMount();
    let attempts = 0;
    server.use(
      http.get(`/api/v1/budgets/${failedMonth}`, () => {
        attempts += 1;
        if (attempts === 1) {
          // Merged t9 interceptor normalizes this to NETWORK_ERROR; the
          // rejection is consumed in-test by the query error state (Q12).
          return HttpResponse.error();
        }
        return HttpResponse.json(anyMonth('2000.00'), { status: 200 });
      })
    );
    renderPage();
    await waitFor(() => {
      const alert = screen.getByRole('alert');
      expect(alert.textContent).toContain('Could not load the budget');
    });
    expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
    expect(screen.queryByTestId('budget-amount')).toBeNull();
    expect(attempts).toBe(1);
  });

  it('retrying the failed budget query refetches through the handler and renders the amount', async () => {
    const failedMonth = pickerValueAtMount();
    let attempts = 0;
    server.use(
      http.get(`/api/v1/budgets/${failedMonth}`, () => {
        attempts += 1;
        if (attempts === 1) {
          return HttpResponse.error();
        }
        return HttpResponse.json(anyMonth('2000.00'), { status: 200 });
      })
    );
    renderPage();
    const retry = await screen.findByRole('button', { name: 'Retry' });
    expect(attempts).toBe(1);
    fireEvent.click(retry);
    await displayLoaded();
    // The retry click RE-INVOKED the query: second hit at the handler.
    expect(attempts).toBe(2);
    expect(screen.queryByRole('alert')).toBeNull();
    expect(screen.getByTestId('budget-amount').textContent).toBe('2000.00');
  });

  it('changing the month picker requests the new year_month path', async () => {
    const seen: string[] = [];
    server.use(
      http.get('/api/v1/budgets/:year_month', ({ request }) => {
        seen.push(new URL(request.url).pathname);
        return HttpResponse.json(anyMonth('2000.00'), { status: 200 });
      })
    );
    renderPage();
    await displayLoaded();
    const initial = pickerValue();
    // The initial mounted query requested the picker's month.
    expect(seen).toContain(`/api/v1/budgets/${initial}`);
    // A month guaranteed different from the clock-derived initial value.
    const target = shiftMonth(initial, -3);
    expect(target).not.toBe(initial);
    fireEvent.change(screen.getByLabelText('Budget month'), { target: { value: target } });
    await waitFor(() => {
      expect(seen).toContain(`/api/v1/budgets/${target}`);
    });
  });

  it('the month picker value follows the YYYY-MM year month shape', async () => {
    const seen: string[] = [];
    server.use(
      http.get('/api/v1/budgets/:year_month', ({ request }) => {
        seen.push(new URL(request.url).pathname);
        return HttpResponse.json(anyMonth('2000.00'), { status: 200 });
      })
    );
    renderPage();
    await displayLoaded();
    const picker = screen.getByLabelText('Budget month') as HTMLInputElement;
    expect(picker.type).toBe('month');
    expect(picker.value).toMatch(/^\d{4}-\d{2}$/);
    // The mounted query requested exactly that value.
    expect(seen).toContain(`/api/v1/budgets/${picker.value}`);
  });

  it('clicking delete budget opens the confirm dialog without calling the delete handler', async () => {
    server.use(
      http.get('/api/v1/budgets/:year_month', () => HttpResponse.json(anyMonth('2000.00')))
    );
    renderPage();
    await displayLoaded();
    const before = callCount('budgets.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete budget' }));
    const dialog = await screen.findByRole('dialog', { name: 'Delete budget' });
    expect(dialog).toBeTruthy();
    // No DELETE request left the page while the dialog is open.
    expect(callCount('budgets.delete')).toBe(before);
    expect(callCount('budgets.delete')).toBe(0);
  });

  it('confirming the delete calls the delete handler and refetches the month', async () => {
    const monthHits: Record<string, number> = {};
    server.use(
      http.get('/api/v1/budgets/:year_month', ({ request }) => {
        const path = new URL(request.url).pathname;
        monthHits[path] = (monthHits[path] ?? 0) + 1;
        return HttpResponse.json(anyMonth('2000.00'), { status: 200 });
      })
    );
    renderPage();
    await displayLoaded();
    const month = pickerValue();
    const monthPath = `/api/v1/budgets/${month}`;
    const hitsBefore = monthHits[monthPath] ?? 0;
    const deleteBefore = callCount('budgets.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete budget' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Confirm' }));
    // Handler actually invoked (count delta, not code reading).
    await waitFor(() => {
      expect(callCount('budgets.delete')).toBe(deleteBefore + 1);
    });
    // REQ-FE-051: the mutation invalidates ["budgets"] -> the mounted
    // month observer refetches through the handler.
    await waitFor(() => {
      expect(monthHits[monthPath] ?? 0).toBeGreaterThan(hitsBefore);
    });
    // Toast-on-success half of REQ-FE-082.
    expect(await screen.findByText('Budget deleted')).toBeTruthy();
  });
});

describe('BudgetPage twelve month history (ac2)', () => {
  it('the history renders twelve month rows ending at the selected month', async () => {
    server.use(
      http.get('/api/v1/budgets/:year_month', () => HttpResponse.json(anyMonth('2000.00')))
    );
    renderPage();
    await displayLoaded();
    const rows = screen.getAllByTestId('budget-history-row');
    expect(rows).toHaveLength(12);
    const labels = rows.map((row) => row.textContent ?? '');
    // Ascending trailing window ending AT the picker month (Q4 contract).
    expect(labels[0]).toContain(shiftMonth(pickerValue(), -11));
    expect(labels[11]).toContain(pickerValue());
    // Strictly ascending months.
    const months = labels.map((label) => label.slice(0, 7));
    expect(months).toEqual(monthWindow(pickerValue()));
  });

  it('the history row renders the amount string or the em dash placeholder per month', async () => {
    const first = pickerValueAtMount();
    const window = monthWindow(first);
    const presentMonth = window[0] ?? '';
    const absentMonth = window[11] ?? '';
    server.use(
      http.get(`/api/v1/budgets/${presentMonth}`, () =>
        HttpResponse.json({ year_month: presentMonth, amount: '12.30' }, { status: 200 })
      ),
      http.get(`/api/v1/budgets/${absentMonth}`, () =>
        HttpResponse.json({ year_month: absentMonth, amount: '0.00' }, { status: 200 })
      )
    );
    renderPage();
    await waitFor(() => {
      const rows = screen.getAllByTestId('budget-history-row');
      expect(within(rows[0] as HTMLElement).getByText('12.30')).toBeTruthy();
    });
    const rows = screen.getAllByTestId('budget-history-row');
    // Present month: the API string verbatim. Absent month: em dash U+2014.
    expect(within(rows[0] as HTMLElement).getByText('12.30')).toBeTruthy();
    expect(within(rows[11] as HTMLElement).getByText('\u2014')).toBeTruthy();
    expect(rows[11]?.textContent).not.toContain('12.30');
  });
});

describe('BudgetPage month window helper (ac2)', () => {
  it('the month window helper walks across the year boundary', () => {
    // Pinned Q4 contract.
    expect(shiftMonth('2026-01', -1)).toBe('2025-12');
    expect(shiftMonth('2026-12', 1)).toBe('2027-01');
    expect(monthWindow('2026-02')).toEqual([
      '2025-03',
      '2025-04',
      '2025-05',
      '2025-06',
      '2025-07',
      '2025-08',
      '2025-09',
      '2025-10',
      '2025-11',
      '2025-12',
      '2026-01',
      '2026-02'
    ]);
  });

  it('the month window helper never mutates the YYYY-MM shape', () => {
    const shape = /^\d{4}-\d{2}$/;
    for (const month of monthWindow('2026-01')) {
      expect(month).toMatch(shape);
    }
    expect(shiftMonth('2026-03', -3)).toBe('2025-12');
    expect(shiftMonth('2026-12', 13)).toBe('2028-01');
    // Zero-padding survives both directions and the year rollover.
    expect(shiftMonth('0001-01', -1)).toBe('0000-12');
    expect(monthWindow('0001-01').every((month) => shape.test(month))).toBe(true);
  });
});

/** The picker's initial value BEFORE any render (the clock-derived month
 * the failing override must target). */
function pickerValueAtMount(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${String(now.getFullYear()).padStart(4, '0')}-${month}`;
}

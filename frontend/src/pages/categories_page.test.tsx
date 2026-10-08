// AC3/AC4: CategoriesPage (REQ-FE-065, REQ-PROD-013/034,
// REQ-FE-100/101/102/103, REQ-SEC-033 — t18). Frozen titles (12 nodes):
// five system-section nodes grepped by ac3, seven custom-section nodes by
// ac4.
//
// Fixtures per Q6: handlers.ts / setup.ts stay UNTOUCHED; the page test
// supplies its own mixed system/custom list via server.use with the pinned
// rows (systemRow = the merged demoCategory, customRow = the same shape
// with is_system:false). The empty-custom node overrides with ONLY the
// system row. The in-use 409 override mirrors the merged backend body
// ({detail, code, field:'category_id'}), and the create/delete proofs are
// merged t16 callCount deltas, not code reading.
//
// Mounts carry their own QueryClient (retry:false, staleTime:0) per the
// STATE/QUERY RULES.

import { beforeEach, describe, expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { server } from '../test/server';
import { ToastProvider } from '../context/toast_context';
import { CategoriesPage } from './categories_page';
import { demoCategory, callCount, callCounts, resetCallCounts } from '../test/handlers';
import type { Category, CategoryList } from '../api/categories';

/** Pinned page fixture (Q6): the merged demoCategory IS the system row. */
const systemRow: Category = { ...demoCategory };

/** Pinned page fixture (Q6): same shape, custom, icon null. */
const customRow: Category = {
  ...systemRow,
  id: 'c2000000-0000-4000-8000-000000000002',
  name: 'Custom',
  icon: null,
  is_system: false
};

const mixedList = (categories: Category[]): CategoryList => ({ categories });

const serveList = (categories: Category[]): void => {
  server.use(
    http.get('/api/v1/categories', () => {
      // Mirror the merged counted handler so callCount('categories.list')
      // deltas stay observable through the override (handlers.ts untouched).
      callCounts['categories.list'] = (callCounts['categories.list'] ?? 0) + 1;
      return HttpResponse.json(mixedList(categories), { status: 200 });
    })
  );
};

const renderPage = (): void => {
  render(
    <ToastProvider>
      <PageProviders>
        <CategoriesPage />
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

/** Wait until the list query has served and the custom section is up. */
const listLoaded = async (): Promise<void> => {
  await waitFor(() => {
    expect(screen.queryByText('System categories')).not.toBeNull();
  });
};

/** Fill the three create-form fields in one sweep. */
const fillCreateForm = (values: { name: string; color: string; icon?: string }): void => {
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: values.name } });
  fireEvent.change(screen.getByLabelText('Color'), { target: { value: values.color } });
  if (values.icon !== undefined) {
    fireEvent.change(screen.getByLabelText('Icon (optional)'), {
      target: { value: values.icon }
    });
  }
};

beforeEach(() => {
  resetCallCounts();
});

describe('CategoriesPage system section (ac3)', () => {
  it('the page sets the Categories document title', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    expect(document.title).toBe('Categories');
  });

  it('a pending category query renders the loading status region', () => {
    serveList([systemRow, customRow]);
    renderPage();
    // Synchronously (before the handler resolves) the role=status region is up.
    const status = screen.getByRole('status');
    expect(status.textContent).toContain('Loading categories');
  });

  it('the system section renders each system category row', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const systemRows = screen.getAllByTestId('system-category-row');
    expect(systemRows).toHaveLength(1);
    expect(systemRows[0]?.textContent).toContain('Food');
    // The custom row never leaks into the system section.
    expect(systemRows[0]?.textContent).not.toContain('Custom');
  });

  it('no system category row renders a delete control', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const systemRows = screen.getAllByTestId('system-category-row');
    // REQ-SEC-033: the affordance is ABSENT from the DOM, not disabled.
    for (const row of systemRows) {
      expect(row.querySelector('button')).toBeNull();
    }
    expect(screen.queryByRole('button', { name: /delete food/i })).toBeNull();
  });

  it('no system category row renders an edit control', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const systemRows = screen.getAllByTestId('system-category-row');
    for (const row of systemRows) {
      expect(row.querySelector('button')).toBeNull();
      expect(row.querySelector('input')).toBeNull();
    }
    expect(screen.queryByRole('button', { name: /edit food/i })).toBeNull();
  });
});

describe('CategoriesPage custom section (ac4)', () => {
  it('the custom section lists only categories with is_system false', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const customRows = screen.getAllByTestId('custom-category-row');
    expect(customRows).toHaveLength(1);
    expect(customRows[0]?.textContent).toContain('Custom');
    expect(customRows[0]?.textContent).not.toContain('Food');
    // The custom row DOES carry the delete affordance.
    expect(screen.getByRole('button', { name: 'Delete Custom' })).toBeTruthy();
  });

  it('an empty custom list renders the no custom categories message', async () => {
    // Q6: the all-system fixture overrides the list handler.
    serveList([systemRow]);
    renderPage();
    expect(
      await screen.findByText('No custom categories yet. Add your first category.')
    ).toBeTruthy();
    expect(screen.queryByTestId('custom-category-row')).toBeNull();
  });

  it('the create form posts name color and icon and refetches the list', async () => {
    serveList([systemRow]);
    let posted: Record<string, unknown> | null = null;
    server.use(
      http.post('/api/v1/categories', async ({ request }) => {
        posted = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ ...customRow, name: 'New' }, { status: 201 });
      })
    );
    renderPage();
    await listLoaded();
    const listBefore = callCount('categories.list');
    // Icon left EMPTY: the payload must OMIT the icon key entirely (Q7).
    fillCreateForm({ name: 'New', color: '#123456' });
    fireEvent.click(screen.getByRole('button', { name: 'Add category' }));
    await waitFor(() => {
      expect(posted).not.toBeNull();
    });
    expect(posted).not.toBeNull();
    const payload = posted as unknown as Record<string, unknown>;
    expect(payload.name).toBe('New');
    expect(payload.color).toBe('#123456');
    expect('icon' in payload).toBe(false);
    // REQ-FE-051: the create mutation invalidates ["categories"] -> the
    // mounted list refetches (observable count delta).
    await waitFor(() => {
      expect(callCount('categories.list')).toBeGreaterThan(listBefore);
    });
    expect(await screen.findByText('Category created')).toBeTruthy();
  });

  it('a duplicate name 409 renders the backend message on the name field', async () => {
    serveList([systemRow]);
    server.use(
      http.post('/api/v1/categories', () =>
        HttpResponse.json(
          { detail: 'Category name already exists', code: 'DUPLICATE_CATEGORY', field: 'name' },
          { status: 409 }
        )
      )
    );
    renderPage();
    await listLoaded();
    fillCreateForm({ name: 'Food', color: '#123456' });
    fireEvent.click(screen.getByRole('button', { name: 'Add category' }));
    // The message lands ON the name field (id pinned in the issue/ac4),
    // not merely in the success/error toast region.
    await waitFor(() => {
      expect(document.getElementById('category-name-error')).not.toBeNull();
    });
    const fieldError = document.getElementById('category-name-error');
    expect(fieldError?.textContent).toBe('Category name already exists');
  });

  it('a delete blocked by the backend surfaces the in-use message', async () => {
    serveList([systemRow, customRow]);
    server.use(
      http.delete('/api/v1/categories/:id', () =>
        HttpResponse.json(
          {
            detail: 'Category is used by expenses',
            code: 'CATEGORY_IN_USE',
            field: 'category_id'
          },
          { status: 409 }
        )
      )
    );
    renderPage();
    await listLoaded();
    fireEvent.click(screen.getByRole('button', { name: 'Delete Custom' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Confirm' }));
    // Q5: field='category_id' is NOT a field on this form, so the verbatim
    // backend string surfaces as a root/row-level role="alert" message.
    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toContain('Category is used by expenses');
    // NOT on the name field.
    expect(document.getElementById('category-name-error')).toBeNull();
  });

  it('clicking delete category opens the confirm dialog without calling the delete handler', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const before = callCount('categories.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete Custom' }));
    const dialog = await screen.findByRole('dialog', { name: 'Delete category' });
    expect(dialog).toBeTruthy();
    // No DELETE request left the page while the dialog is open.
    expect(callCount('categories.delete')).toBe(before);
    expect(callCount('categories.delete')).toBe(0);
  });

  it('confirming the delete calls the delete handler and refetches the list', async () => {
    serveList([systemRow, customRow]);
    renderPage();
    await listLoaded();
    const listBefore = callCount('categories.list');
    const deleteBefore = callCount('categories.delete');
    fireEvent.click(screen.getByRole('button', { name: 'Delete Custom' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Confirm' }));
    // Handler actually invoked (count delta, not code reading).
    await waitFor(() => {
      expect(callCount('categories.delete')).toBe(deleteBefore + 1);
    });
    // REQ-FE-051: the mutation invalidates ["categories"] -> refetch.
    await waitFor(() => {
      expect(callCount('categories.list')).toBeGreaterThan(listBefore);
    });
    expect(await screen.findByText('Category deleted')).toBeTruthy();
  });
});

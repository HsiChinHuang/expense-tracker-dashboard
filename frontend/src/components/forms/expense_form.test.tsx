// AC3: ExpenseForm modal (REQ-FE-081/082, REQ-FE-111 — t17). Frozen
// titles (9 nodes): create posts the decimal STRING + resets, edit
// prefills/submits the change, client blocks before network (t9 ac4
// callCount-0 pattern), blur validation for decimals/max, submit disabled
// while pending, backend {field} mapping, values preserved on failure,
// focus into the modal on open / back to the trigger on close.
//
// The form is presentational: the harness owns submission through the
// real use_expense_mutations hooks (handler traffic is counted by the
// merged t16 handlers.ts). Mounts carry their own QueryClient with
// retry:false, staleTime:0 per the issue STATE/QUERY RULES.

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { server } from '../../test/server';
import { ExpenseForm } from './expense_form';
import type { ExpenseSubmitResult } from './expense_form';
import { use_expense_mutations } from '../../hooks/use_expenses';
import { demoCategory, demoExpense, callCount, resetCallCounts } from '../../test/handlers';
import type { Category } from '../../api/categories';
import type { Expense } from '../../api/expenses';
import { toApiError, type ApiError } from '../../api/client';
import type { ExpenseFormValues } from '../../utils/validation';

// t73: the category control is a <select> of names fed by use_categories.
// The shared fixture stays FROZEN (one category: demoCategory 'Food'), so
// multi-category coverage goes through per-test server.use overrides only.
const customCategory: Category = {
  id: 'c9000000-0000-4000-8000-000000000009',
  name: 'Vinyl Records',
  color: '#8B5CF6',
  icon: null,
  is_system: false,
  created_at: '2026-02-01T00:00:00Z'
};

const COMPLETE: ExpenseFormValues = {
  amount: '42.50',
  category_id: demoCategory.id,
  date: '2026-02-05',
  note: 'lunch'
};

/** Fill the four fields in one sweep. */
const fillForm = async (values: Partial<ExpenseFormValues>): Promise<void> => {
  if (values.amount !== undefined) {
    fireEvent.change(screen.getByLabelText('Amount'), { target: { value: values.amount } });
  }
  if (values.category_id !== undefined) {
    // t73 P1 REWRITE (title kept): the control is a <select> of names now -
    // fireEvent.change works on <select>; the option must exist before the
    // change lands, so the categories query is awaited first.
    await screen.findByText(demoCategory.name, { selector: 'option' });
    fireEvent.change(screen.getByLabelText('Category'), {
      target: { value: values.category_id }
    });
  }
  if (values.date !== undefined) {
    fireEvent.change(screen.getByLabelText('Date'), { target: { value: values.date } });
  }
  if (values.note !== undefined) {
    fireEvent.change(screen.getByLabelText('Note'), { target: { value: values.note } });
  }
};

const submitButton = (): HTMLButtonElement =>
  screen.getByRole('button', { name: /add expense/i }) as HTMLButtonElement;

/** Harness: real mutation hooks behind the onSubmit contract. */
const MutationHarness = ({ onCancel }: { onCancel: () => void }): JSX.Element => {
  const { update } = use_expense_mutations();
  const handleEdit = async (values: ExpenseFormValues): Promise<ExpenseSubmitResult> => {
    try {
      await update.mutateAsync({ id: demoExpense.id, payload: { amount: values.amount } });
      return { ok: true };
    } catch (error) {
      return { ok: false, error: toApiError(error) };
    }
  };
  return <ExpenseForm expense={demoExpense} onSubmit={handleEdit} onCancel={onCancel} />;
};

const CreateHarness = ({
  onSubmit,
  onCancel,
  expense
}: {
  onSubmit: (values: ExpenseFormValues) => Promise<ExpenseSubmitResult>;
  onCancel: () => void;
  expense?: Expense;
}): JSX.Element => (
  <ExpenseForm {...(expense ? { expense } : {})} onSubmit={onSubmit} onCancel={onCancel} />
);

/** Per-mount QueryClient with the pinned options (STATE/QUERY RULES).
 * MemoryRouter wraps the tree so the /categories hint Link never renders
 * outside a router context. */
const QueryProviders = ({ children }: { children: ReactNode }): JSX.Element => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return (
    <MemoryRouter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
};

/** Harness whose mutations hang forever — pins isSubmitting. */
const PendingHarness = ({ onCancel }: { onCancel: () => void }): JSX.Element => {
  const [pending] = useState<Promise<ExpenseSubmitResult>>(
    () => new Promise<ExpenseSubmitResult>(() => undefined)
  );
  const handleSubmit = (): Promise<ExpenseSubmitResult> => pending;
  return <ExpenseForm onSubmit={handleSubmit} onCancel={onCancel} />;
};

/** Create harness on the real mutation hooks, closable by the parent. */
const ClosableCreateHarness = ({
  onClosed
}: {
  onClosed: () => void;
}): JSX.Element => {
  const [open, setOpen] = useState(true);
  const { create } = use_expense_mutations();
  const handleSubmit = async (values: ExpenseFormValues): Promise<ExpenseSubmitResult> => {
    try {
      await create.mutateAsync({
        amount: values.amount,
        category_id: values.category_id,
        date: values.date,
        ...(values.note ? { note: values.note } : {})
      });
      return { ok: true };
    } catch (error) {
      return { ok: false, error: toApiError(error) };
    }
  };
  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)}>
        reopen
      </button>
    );
  }
  return (
    <ExpenseForm
      onSubmit={handleSubmit}
      onCancel={() => {
        setOpen(false);
        onClosed();
      }}
    />
  );
};

const okResult = (): Promise<ExpenseSubmitResult> => Promise.resolve({ ok: true });

const failingSubmit = (error: ApiError) => (): Promise<ExpenseSubmitResult> =>
  Promise.resolve({ ok: false, error });

/** Success-on-submit harness used by the focus test (no network needed). */
const ClosableFocusHarness = ({ onClosed }: { onClosed: () => void }): JSX.Element => {
  const [open, setOpen] = useState(true);
  if (!open) {
    return <span>closed</span>;
  }
  return (
    <CreateHarness
      onSubmit={async () => {
        setOpen(false);
        onClosed();
        return okResult();
      }}
      onCancel={() => {
        setOpen(false);
        onClosed();
      }}
    />
  );
};

beforeEach(() => {
  resetCallCounts();
});

describe('ExpenseForm create/edit (ac3)', () => {
  it('the create form posts the amount as a decimal string and resets on success', async () => {
    const posted: { body: { amount?: unknown } | null; type: string | null } = {
      body: null,
      type: null
    };
    server.use(
      http.post('/api/v1/expenses', async ({ request }) => {
        posted.body = (await request.json()) as { amount?: unknown };
        posted.type = typeof posted.body.amount;
        return HttpResponse.json({ ...demoExpense, amount: '42.50' }, { status: 201 });
      })
    );
    let closed = 0;
    render(
      <QueryProviders>
        <ClosableCreateHarness
          onClosed={() => {
            closed += 1;
          }}
        />
      </QueryProviders>
    );
    await fillForm(COMPLETE);
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(posted.body).not.toBeNull();
    });
    // The wire value is the decimal STRING, never a number (REQ-PROD-023).
    expect(posted.body?.amount).toBe('42.50');
    expect(posted.type).toBe('string');
    // Success path: the parent closed the modal and the form reset.
    await waitFor(() => {
      expect(closed).toBe(1);
    });
    expect(screen.queryByLabelText('Amount')).toBeNull();
    // Reopening shows the cleared defaults, not the submitted values.
    fireEvent.click(screen.getByRole('button', { name: 'reopen' }));
    const amount = screen.getByLabelText('Amount') as HTMLInputElement;
    expect(amount.value).toBe('');
  });

  it('the edit form prefills existing values and submits the changed amount', async () => {
    let postedAmount: unknown = null;
    server.use(
      http.put('/api/v1/expenses/:id', async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        postedAmount = body.amount;
        return HttpResponse.json({ ...demoExpense, amount: '99.99' }, { status: 200 });
      })
    );
    render(
      <QueryProviders>
        <MutationHarness onCancel={() => undefined} />
      </QueryProviders>
    );
    const amount = screen.getByLabelText('Amount') as HTMLInputElement;
    const date = screen.getByLabelText('Date') as HTMLInputElement;
    const note = screen.getByLabelText('Note') as HTMLTextAreaElement;
    // Prefill comes from the passed expense, verbatim.
    expect(amount.value).toBe(demoExpense.amount);
    expect(date.value).toBe(demoExpense.date);
    expect(note.value).toBe('groceries');
    fireEvent.change(amount, { target: { value: '99.99' } });
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));
    await waitFor(() => {
      expect(postedAmount).toBe('99.99');
    });
  });

  it('an invalid amount blocks submission before any network request', async () => {
    const onSubmit = vi.fn(async (): Promise<ExpenseSubmitResult> => okResult());
    render(
      <QueryProviders>
        <CreateHarness onSubmit={onSubmit} onCancel={() => undefined} />
      </QueryProviders>
    );
    await fillForm({ ...COMPLETE, amount: 'abc' });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(
        screen.getByText('Amount must be a positive number with at most 2 decimals')
      ).toBeTruthy();
    });
    // Client-side block: neither the submit handler nor the handler ran.
    expect(onSubmit).not.toHaveBeenCalled();
    expect(callCount('expenses.create')).toBe(0);
  });

  it('amount with three decimals fails validation on blur', async () => {
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    const amount = screen.getByLabelText('Amount');
    fireEvent.change(amount, { target: { value: '1.234' } });
    fireEvent.blur(amount);
    expect(
      await screen.findByText('Amount must be a positive number with at most 2 decimals')
    ).toBeTruthy();
  });

  it('an amount above the maximum fails validation on blur', async () => {
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    const amount = screen.getByLabelText('Amount');
    fireEvent.change(amount, { target: { value: '10000000000.00' } });
    fireEvent.blur(amount);
    expect(await screen.findByText('Amount must be 9999999999.99 or less')).toBeTruthy();
  });

  it('submit is disabled while the mutation is pending', async () => {
    render(
      <QueryProviders>
        <PendingHarness onCancel={() => undefined} />
      </QueryProviders>
    );
    expect(submitButton().disabled).toBe(false);
    await fillForm(COMPLETE);
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(submitButton().disabled).toBe(true);
    });
  });

  it('a backend field error is mapped onto the named form field', async () => {
    const serverError: ApiError = {
      status: 422,
      code: 'VALIDATION_ERROR',
      message: 'amount must be positive',
      field: 'amount'
    };
    render(
      <QueryProviders>
        <CreateHarness onSubmit={failingSubmit(serverError)} onCancel={() => undefined} />
      </QueryProviders>
    );
    await fillForm(COMPLETE);
    fireEvent.click(submitButton());
    expect(await screen.findByText('amount must be positive')).toBeTruthy();
  });

  it('form values are preserved when the create mutation fails', async () => {
    const serverError: ApiError = {
      status: 409,
      code: 'CONFLICT',
      message: 'expense conflicts with a locked budget'
    };
    render(
      <QueryProviders>
        <CreateHarness onSubmit={failingSubmit(serverError)} onCancel={() => undefined} />
      </QueryProviders>
    );
    await fillForm(COMPLETE);
    fireEvent.click(submitButton());
    expect(await screen.findByText('expense conflicts with a locked budget')).toBeTruthy();
    // Nothing was cleared or reset (REQ-FE-082).
    expect((screen.getByLabelText('Amount') as HTMLInputElement).value).toBe('42.50');
    // t73 P2 REWRITE (title kept): same observable - the selection survived
    // the failed submit - on the new <select> markup.
    expect((screen.getByLabelText('Category') as HTMLSelectElement).value).toBe(
      demoCategory.id
    );
    expect((screen.getByLabelText('Date') as HTMLInputElement).value).toBe('2026-02-05');
    expect((screen.getByLabelText('Note') as HTMLTextAreaElement).value).toBe('lunch');
  });

  it('focus moves into the modal on open and returns to the trigger on close', async () => {
    const trigger = document.createElement('button');
    trigger.textContent = 'open form';
    document.body.appendChild(trigger);
    trigger.focus();
    expect(document.activeElement).toBe(trigger);
    let closed = 0;
    render(
      <QueryProviders>
        <ClosableFocusHarness onClosed={() => { closed += 1; }} />
      </QueryProviders>
    );
    // Focus moved into the modal (the first field).
    await waitFor(() => {
      expect(document.activeElement).toBe(screen.getByLabelText('Amount'));
    });
    await fillForm(COMPLETE);
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(closed).toBe(1);
    });
    // Focus returned to the trigger when the modal unmounted.
    expect(document.activeElement).toBe(trigger);
    document.body.removeChild(trigger);
  });

  // ---------------------------------------------------------------------
  // t73: the category select (7 new nodes). The nine titles above stay
  // byte-identical (stored gate tests[88] replays them); these nodes are
  // the ac1/ac2/ac3 additions named in the card.
  // ---------------------------------------------------------------------

  it('the category field is a labelled select rather than a text input', async () => {
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    await screen.findByText(demoCategory.name, { selector: 'option' });
    // The control is a <select> whose label is the exact text Category.
    const select = screen.getByLabelText('Category', { selector: 'select' });
    expect(select.tagName).toBe('SELECT');
    // The old bare text input is gone: no 'Category id' label, no text
    // input carrying the category field.
    expect(screen.queryByText('Category id')).toBeNull();
    expect(screen.queryByLabelText('Category id')).toBeNull();
    expect(document.querySelector('input[name="category_id"]')).toBeNull();
    // The htmlFor association is kept on the select itself.
    expect(select.id).toBe('expense-category');
    expect(document.querySelector('label[for="expense-category"]')).not.toBeNull();
  });

  it('the category select lists category names from the categories query and submits the selected id', async () => {
    const posted: { category_id: string | null } = { category_id: null };
    server.use(
      http.post('/api/v1/expenses', async ({ request }) => {
        const body = (await request.json()) as { category_id?: string };
        posted.category_id = body.category_id ?? null;
        return HttpResponse.json({ ...demoExpense }, { status: 201 });
      })
    );
    render(
      <QueryProviders>
        <ClosableCreateHarness onClosed={() => undefined} />
      </QueryProviders>
    );
    // The option list comes from the categories query: one placeholder
    // plus one option per category, each showing the NAME as its text.
    await screen.findByText(demoCategory.name, { selector: 'option' });
    const select = screen.getByLabelText('Category', {
      selector: 'select'
    }) as HTMLSelectElement;
    const options = Array.from(select.options);
    expect(options).toHaveLength(2);
    expect(options[0]?.value).toBe('');
    expect(options[1]?.text).toBe(demoCategory.name);
    expect(options[1]?.value).toBe(demoCategory.id);
    // Selecting the name and submitting carries the row's category_id.
    fireEvent.change(select, { target: { value: demoCategory.id } });
    expect(select.value).toBe(demoCategory.id);
    fireEvent.change(screen.getByLabelText('Amount'), { target: { value: '10.00' } });
    fireEvent.change(screen.getByLabelText('Date'), { target: { value: '2026-02-05' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(posted.category_id).not.toBeNull();
    });
    expect(posted.category_id).toBe(demoCategory.id);
  });

  it('the category select renders both system and custom names from a per-test override', async () => {
    // Two-category coverage through a per-test server.use override only -
    // the shared fixture frontend/src/test/handlers.ts stays FROZEN.
    server.use(
      http.get('/api/v1/categories', () => {
        return HttpResponse.json(
          { categories: [demoCategory, customCategory] },
          { status: 200 }
        );
      })
    );
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    await screen.findByText(customCategory.name, { selector: 'option' });
    const select = screen.getByLabelText('Category', {
      selector: 'select'
    }) as HTMLSelectElement;
    const names = Array.from(select.options).map((option) => option.text);
    expect(names).toEqual(['Select a category', demoCategory.name, customCategory.name]);
    // The custom row is selectable and carries its own id, not the system one.
    const custom = Array.from(select.options).find(
      (option) => option.text === customCategory.name
    );
    expect(custom?.value).toBe(customCategory.id);
  });

  it('the edit form preselects the category of the expense being edited', async () => {
    render(
      <QueryProviders>
        <CreateHarness
          expense={demoExpense}
          onSubmit={async () => okResult()}
          onCancel={() => undefined}
        />
      </QueryProviders>
    );
    // The option arrives asynchronously; the controlled select lands on
    // the edited expense's category_id once it renders.
    await screen.findByText(demoCategory.name, { selector: 'option' });
    const select = screen.getByLabelText('Category', {
      selector: 'select'
    }) as HTMLSelectElement;
    expect(select.value).toBe(demoExpense.category_id);
    expect(select.selectedOptions[0]?.text).toBe(demoCategory.name);
  });

  it('an unset category blocks submission with the required error before any network request', async () => {
    const onSubmit = vi.fn(async (): Promise<ExpenseSubmitResult> => okResult());
    render(
      <QueryProviders>
        <CreateHarness onSubmit={onSubmit} onCancel={() => undefined} />
      </QueryProviders>
    );
    // Everything except the category is filled: the placeholder option
    // ('') is the default selection.
    await screen.findByText(demoCategory.name, { selector: 'option' });
    fireEvent.change(screen.getByLabelText('Amount'), { target: { value: '42.50' } });
    fireEvent.change(screen.getByLabelText('Date'), { target: { value: '2026-02-05' } });
    fireEvent.change(screen.getByLabelText('Note'), { target: { value: 'lunch' } });
    fireEvent.click(submitButton());
    // The existing zod min(1) message renders under the field (validation.ts untouched).
    expect(await screen.findByText('Category is required')).toBeTruthy();
    // Client-side block (t9 ac4 callCount-0 pattern): no handler, no submit.
    expect(onSubmit).not.toHaveBeenCalled();
    expect(callCount('expenses.create')).toBe(0);
  });

  it('the category hint points at the categories page when the list offers no suitable category', async () => {
    // Negative control FIRST on the frozen fixture: with one category
    // loaded, no hint line is rendered.
    const loadedView = render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    await screen.findByText(demoCategory.name, { selector: 'option' });
    expect(screen.queryByText(/no suitable category/i)).toBeNull();
    loadedView.unmount();
    // Per-test override (the shared fixture stays FROZEN): the loaded list
    // is empty, so nothing is pickable and the hint names the merged
    // /categories route (never an invented route).
    server.use(
      http.get('/api/v1/categories', () => {
        return HttpResponse.json({ categories: [] }, { status: 200 });
      })
    );
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    const hint = await screen.findByText(/no suitable category/i);
    expect(hint.textContent).toContain('/categories');
  });

  it('the category select shows a loading status while the categories query is pending and an error retry when it fails', async () => {
    // Pending: a categories request that never resolves keeps the query
    // pending, so the role="status" line shows and no select is offered.
    const unresolvable = new Promise<never>(() => undefined);
    server.use(http.get('/api/v1/categories', () => unresolvable));
    const pendingView = render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    expect(await screen.findByRole('status')).toBeTruthy();
    expect(screen.queryByLabelText('Category', { selector: 'select' })).toBeNull();
    pendingView.unmount();

    // Failed: the categories query errors, so a role="alert" line with a
    // Retry button shows (the merged t17 / expenses_page convention).
    server.use(
      http.get('/api/v1/categories', () => {
        return HttpResponse.json(
          { detail: 'categories unavailable', code: 'UPSTREAM', field: null },
          { status: 503 }
        );
      })
    );
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    const alert = await screen.findByRole('alert');
    expect(alert.textContent).toContain('Could not load categories');
    expect(screen.queryByLabelText('Category', { selector: 'select' })).toBeNull();

    // Retry: the Retry button refetches - the select renders once the
    // request succeeds again.
    server.use(
      http.get('/api/v1/categories', () => {
        return HttpResponse.json({ categories: [demoCategory] }, { status: 200 });
      })
    );
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    });
    await screen.findByText(demoCategory.name, { selector: 'option' });
    expect(screen.getByLabelText('Category', { selector: 'select' })).toBeTruthy();
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

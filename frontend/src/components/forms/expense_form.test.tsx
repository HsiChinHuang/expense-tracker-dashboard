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
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { server } from '../../test/server';
import { ExpenseForm } from './expense_form';
import type { ExpenseSubmitResult } from './expense_form';
import { use_expense_mutations } from '../../hooks/use_expenses';
import { demoCategory, demoExpense, callCount, resetCallCounts } from '../../test/handlers';
import { toApiError, type ApiError } from '../../api/client';
import type { ExpenseFormValues } from '../../utils/validation';

const COMPLETE: ExpenseFormValues = {
  amount: '42.50',
  category_id: demoCategory.id,
  date: '2026-02-05',
  note: 'lunch'
};

/** Fill the four fields in one sweep. */
const fillForm = (values: Partial<ExpenseFormValues>): void => {
  if (values.amount !== undefined) {
    fireEvent.change(screen.getByLabelText('Amount'), { target: { value: values.amount } });
  }
  if (values.category_id !== undefined) {
    fireEvent.change(screen.getByLabelText('Category id'), {
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
  onCancel
}: {
  onSubmit: (values: ExpenseFormValues) => Promise<ExpenseSubmitResult>;
  onCancel: () => void;
}): JSX.Element => <ExpenseForm onSubmit={onSubmit} onCancel={onCancel} />;

/** Per-mount QueryClient with the pinned options (STATE/QUERY RULES). */
const QueryProviders = ({ children }: { children: ReactNode }): JSX.Element => {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: 0 } }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
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
    fillForm(COMPLETE);
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
    fillForm({ ...COMPLETE, amount: 'abc' });
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
    fillForm(COMPLETE);
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
    fillForm(COMPLETE);
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
    fillForm(COMPLETE);
    fireEvent.click(submitButton());
    expect(await screen.findByText('expense conflicts with a locked budget')).toBeTruthy();
    // Nothing was cleared or reset (REQ-FE-082).
    expect((screen.getByLabelText('Amount') as HTMLInputElement).value).toBe('42.50');
    expect((screen.getByLabelText('Category id') as HTMLInputElement).value).toBe(
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
    fillForm(COMPLETE);
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(closed).toBe(1);
    });
    // Focus returned to the trigger when the modal unmounted.
    expect(document.activeElement).toBe(trigger);
    document.body.removeChild(trigger);
  });
});

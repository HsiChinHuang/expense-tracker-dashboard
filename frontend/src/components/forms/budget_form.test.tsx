// AC1: BudgetForm modal (REQ-FE-080/082, REQ-FE-111 — t18). Frozen titles
// (8 nodes): the upsert payload is the decimal STRING + reset on success,
// prefill from the query's amount string, client blocks before network
// (callCount-0 pattern), blur validation for decimals/max through the
// REUSED merged amountSchema, submit disabled while pending, values
// preserved on failure, focus into the modal on open / back to the trigger
// on close. Six of these titles reuse t17's frozen wording verbatim (the
// grep is per-file) — the mechanics are the merged expense_form patterns.
//
// The form is presentational: the harness owns submission through the real
// use_budget_mutations hooks (handler traffic is counted by the merged t16
// handlers.ts). Mounts carry their own QueryClient with retry:false,
// staleTime:0 per the issue STATE/QUERY RULES.

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { server } from '../../test/server';
import { BudgetForm } from './budget_form';
import type { BudgetSubmitResult } from './budget_form';
import { use_budget_mutations } from '../../hooks/use_budget';
import { demoBudget, callCount, resetCallCounts } from '../../test/handlers';
import { toApiError, type ApiError } from '../../api/client';
import type { BudgetFormValues } from '../../utils/validation';

const MONTH = '2026-02';

const amountInput = (): HTMLInputElement =>
  screen.getByLabelText('Amount') as HTMLInputElement;

const submitButton = (): HTMLButtonElement =>
  screen.getByRole('button', { name: /save budget/i }) as HTMLButtonElement;

/** Harness: real upsert hooks behind the onSubmit contract. */
const UpsertHarness = ({
  currentAmount,
  onCancel
}: {
  currentAmount?: string;
  onCancel: () => void;
}): JSX.Element => {
  const { set } = use_budget_mutations(MONTH);
  const handleSubmit = async (values: BudgetFormValues): Promise<BudgetSubmitResult> => {
    try {
      await set.mutateAsync(values.amount);
      return { ok: true };
    } catch (error) {
      return { ok: false, error: toApiError(error) };
    }
  };
  return (
    <BudgetForm
      {...(currentAmount !== undefined ? { currentAmount } : {})}
      yearMonth={MONTH}
      onSubmit={handleSubmit}
      onCancel={onCancel}
    />
  );
};

const CreateHarness = ({
  onSubmit,
  onCancel
}: {
  onSubmit: (values: BudgetFormValues) => Promise<BudgetSubmitResult>;
  onCancel: () => void;
}): JSX.Element => <BudgetForm yearMonth={MONTH} onSubmit={onSubmit} onCancel={onCancel} />;

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

/** Harness whose mutation hangs forever — pins isSubmitting. */
const PendingHarness = ({ onCancel }: { onCancel: () => void }): JSX.Element => {
  const [pending] = useState<Promise<BudgetSubmitResult>>(
    () => new Promise<BudgetSubmitResult>(() => undefined)
  );
  const handleSubmit = (): Promise<BudgetSubmitResult> => pending;
  return <BudgetForm yearMonth={MONTH} onSubmit={handleSubmit} onCancel={onCancel} />;
};

/** Create harness on the real upsert hook, closable by the parent. */
const ClosableHarness = ({
  currentAmount,
  onClosed
}: {
  currentAmount?: string;
  onClosed: () => void;
}): JSX.Element => {
  const [open, setOpen] = useState(true);
  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)}>
        reopen
      </button>
    );
  }
  return (
    <UpsertHarness
      {...(currentAmount !== undefined ? { currentAmount } : {})}
      onCancel={() => {
        setOpen(false);
        onClosed();
      }}
    />
  );
};

const okResult = (): Promise<BudgetSubmitResult> => Promise.resolve({ ok: true });

const failingSubmit = (error: ApiError) => (): Promise<BudgetSubmitResult> =>
  Promise.resolve({ ok: false, error });

beforeEach(() => {
  resetCallCounts();
});

describe('BudgetForm set and edit (ac1)', () => {
  it('the form submits the amount as a decimal string and resets on success', async () => {
    const posted: { body: { amount?: unknown } | null; type: string | null } = {
      body: null,
      type: null
    };
    server.use(
      http.put(`/api/v1/budgets/${MONTH}`, async ({ request }) => {
        posted.body = (await request.json()) as { amount?: unknown };
        posted.type = typeof posted.body.amount;
        return HttpResponse.json({ year_month: MONTH, amount: '42.50' }, { status: 200 });
      })
    );
    let closed = 0;
    render(
      <QueryProviders>
        <ClosableHarness
          onClosed={() => {
            closed += 1;
          }}
        />
      </QueryProviders>
    );
    fireEvent.change(amountInput(), { target: { value: '42.50' } });
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
    // Reopening shows the cleared defaults, not the submitted value.
    fireEvent.click(screen.getByRole('button', { name: 'reopen' }));
    expect(amountInput().value).toBe('');
  });

  it('the form prefills the existing amount when a budget is present', async () => {
    let postedAmount: unknown = null;
    server.use(
      http.put(`/api/v1/budgets/${MONTH}`, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        postedAmount = body.amount;
        return HttpResponse.json({ year_month: MONTH, amount: '99.99' }, { status: 200 });
      })
    );
    render(
      <QueryProviders>
        <UpsertHarness currentAmount={demoBudget.amount} onCancel={() => undefined} />
      </QueryProviders>
    );
    // Prefill comes from the query's amount string, verbatim (Q10).
    expect(amountInput().value).toBe('2000.00');
    fireEvent.change(amountInput(), { target: { value: '99.99' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(postedAmount).toBe('99.99');
    });
  });

  it('an invalid amount blocks submission before any network request', async () => {
    const onSubmit = vi.fn(async (): Promise<BudgetSubmitResult> => okResult());
    render(
      <QueryProviders>
        <CreateHarness onSubmit={onSubmit} onCancel={() => undefined} />
      </QueryProviders>
    );
    fireEvent.change(amountInput(), { target: { value: 'abc' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(
        screen.getByText('Amount must be a positive number with at most 2 decimals')
      ).toBeTruthy();
    });
    // Client-side block: neither the submit handler nor the handler ran.
    expect(onSubmit).not.toHaveBeenCalled();
    expect(callCount('budgets.set')).toBe(0);
  });

  it('amount with three decimals fails validation on blur', async () => {
    render(
      <QueryProviders>
        <CreateHarness onSubmit={async () => okResult()} onCancel={() => undefined} />
      </QueryProviders>
    );
    const amount = amountInput();
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
    const amount = amountInput();
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
    fireEvent.change(amountInput(), { target: { value: '42.50' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(submitButton().disabled).toBe(true);
    });
  });

  it('form values are preserved when the save mutation fails', async () => {
    const serverError: ApiError = {
      status: 422,
      code: 'VALIDATION_ERROR',
      message: 'amount must be positive'
    };
    render(
      <QueryProviders>
        <CreateHarness onSubmit={failingSubmit(serverError)} onCancel={() => undefined} />
      </QueryProviders>
    );
    fireEvent.change(amountInput(), { target: { value: '42.50' } });
    fireEvent.click(submitButton());
    expect(await screen.findByText('amount must be positive')).toBeTruthy();
    // Nothing was cleared or reset (REQ-FE-082).
    expect(amountInput().value).toBe('42.50');
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
        <ClosableHarness
          onClosed={() => {
            closed += 1;
          }}
        />
      </QueryProviders>
    );
    // Focus moved into the modal (the first field).
    await waitFor(() => {
      expect(document.activeElement).toBe(amountInput());
    });
    // Closing the modal (parent unmounts it) returns focus to the trigger.
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    await waitFor(() => {
      expect(closed).toBe(1);
    });
    expect(screen.queryByLabelText('Amount')).toBeNull();
    expect(document.activeElement).toBe(trigger);
    document.body.removeChild(trigger);
  });
});

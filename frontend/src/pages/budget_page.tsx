// BudgetPage — the budget vertical slice (REQ-FE-064, REQ-PROD-012,
// REQ-FE-100/101/102/103, REQ-FE-015, t18).
//
// Data access goes through the merged t16 hooks ONLY (REQ-ARCH-012): one
// use_budget(yearMonth) drives the display, use_budget_mutations(yearMonth)
// performs the PUT upsert (create and edit are the SAME mutation — budgets
// have no id, Q10) and the DELETE. The 12-month history composes from the
// per-month contract (no backend list endpoint exists in §7.6): twelve
// mounted use_budget observers over the trailing window, each keyed under
// queryKeys.budgets.byMonth — every key is a prefix member of
// queryKeys.budgets.root, so any set/remove invalidation refreshes the
// whole window for free (Q3). useQueries is NOT used.
//
// Money renders from the API string verbatim (REQ-PROD-023); an absent
// month is the string "0.00", which renders the pinned empty state and
// hides the delete affordance entirely (Q9 — DELETE on an absent month
// 404s, a disabled button invites the click). Loading/error/empty states
// are the inline t17 conventions: role="status", role="alert" + Retry
// (query.refetch()), plain <p>. No ErrorState/EmptyState components (Q8).

import { useEffect, useState } from 'react';
import { use_budget, use_budget_mutations } from '../hooks/use_budget';
import { ConfirmDialog } from '../components/ui/confirm_dialog';
import { BudgetForm } from '../components/forms/budget_form';
import type { BudgetSubmitResult } from '../components/forms/budget_form';
import { useToast } from '../context/toast_context';
import { toApiError } from '../api/client';
import type { BudgetFormValues } from '../utils/validation';

/** Placeholder for an absent history month — em dash U+2014, NOT a hyphen. */
export const EMPTY_HISTORY_PLACEHOLDER = '\u2014';

/** Months in the trailing history window (REQ-FE-064: twelve). */
const HISTORY_MONTHS = 12;

/** Current wall-clock month as YYYY-MM (the picker's initial value). */
const currentMonth = (): string => {
  const now = new Date();
  const year = String(now.getFullYear());
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
};

/** Shift a YYYY-MM string by `delta` months (stdlib integer math only —
 * date-fns is BANNED, Q4). Never mutates the YYYY-MM shape. */
export const shiftMonth = (yearMonth: string, delta: number): string => {
  const [yearText, monthText] = yearMonth.split('-');
  const index = Number(yearText) * 12 + (Number(monthText) - 1) + delta;
  const year = Math.floor(index / 12);
  const month = (index % 12 + 12) % 12 + 1;
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}`;
};

/** Twelve ascending YYYY-MM months ENDING at `endMonth` (inclusive). */
export const monthWindow = (endMonth: string): string[] => {
  const months: string[] = [];
  for (let back = HISTORY_MONTHS - 1; back >= 0; back -= 1) {
    months.push(shiftMonth(endMonth, -back));
  }
  return months;
};

export const BudgetPage = (): JSX.Element => {
  const { showToast } = useToast();
  const [yearMonth, setYearMonth] = useState(currentMonth);
  const [formOpen, setFormOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const budget = use_budget(yearMonth);
  const { set, remove } = use_budget_mutations(yearMonth);
  const historyMonths = monthWindow(yearMonth);

  useEffect(() => {
    document.title = 'Budget';
  }, []);

  const amount = budget.data?.amount;
  const absent = amount === '0.00';

  const submitForm = async (values: BudgetFormValues): Promise<BudgetSubmitResult> => {
    try {
      await set.mutateAsync(values.amount);
      showToast('Budget saved', 'success');
      return { ok: true };
    } catch (error) {
      const apiError = toApiError(error);
      showToast(apiError.message, 'error');
      return { ok: false, error: apiError };
    }
  };

  const confirmDelete = async (): Promise<void> => {
    setConfirmOpen(false);
    try {
      await remove.mutateAsync();
      showToast('Budget deleted', 'success');
    } catch (error) {
      showToast(toApiError(error).message, 'error');
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Budget</h1>
        <button
          type="button"
          className="rounded bg-slate-800 px-3 py-1 text-white"
          onClick={() => {
            setFormOpen(true);
          }}
        >
          {absent ? 'Set budget' : 'Edit budget'}
        </button>
      </div>

      <div className="mt-4">
        <label className="text-sm text-slate-700">
          Month
          <input
            aria-label="Budget month"
            type="month"
            className="ml-2 rounded border border-slate-300 p-1"
            value={yearMonth}
            onChange={(event) => {
              setYearMonth(event.target.value);
            }}
          />
        </label>
      </div>

      {budget.isPending ? (
        <p role="status" className="mt-4 text-slate-600">
          Loading budget…
        </p>
      ) : null}

      {budget.isError ? (
        <div role="alert" className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">
          <p>Could not load the budget. The server may be unreachable.</p>
          <button
            type="button"
            className="mt-2 rounded border border-red-300 px-2 py-1"
            onClick={() => {
              void budget.refetch();
            }}
          >
            Retry
          </button>
        </div>
      ) : null}

      {!budget.isPending && !budget.isError && budget.data && absent ? (
        <p className="mt-4 text-slate-600">No budget yet. Set a budget to start tracking.</p>
      ) : null}

      {!budget.isPending && !budget.isError && budget.data && !absent ? (
        <div className="mt-4">
          <p className="text-sm text-slate-700">
            Budget for {yearMonth}: <span data-testid="budget-amount">{budget.data.amount}</span>
          </p>
          <button
            type="button"
            className="mt-2 underline text-red-700"
            onClick={() => {
              setConfirmOpen(true);
            }}
          >
            Delete budget
          </button>
        </div>
      ) : null}

      <h2 className="mt-8 text-lg font-semibold text-slate-900">Budget history</h2>
      <ul className="mt-2 space-y-1 text-sm text-slate-700">
        {historyMonths.map((month) => (
          <HistoryRow key={month} month={month} />
        ))}
      </ul>

      {formOpen ? (
        <BudgetForm
          {...(budget.data ? { currentAmount: budget.data.amount } : {})}
          yearMonth={yearMonth}
          onSubmit={submitForm}
          onCancel={() => {
            setFormOpen(false);
          }}
        />
      ) : null}

      <ConfirmDialog
        open={confirmOpen}
        title="Delete budget"
        onConfirm={() => {
          void confirmDelete();
        }}
        onCancel={() => {
          setConfirmOpen(false);
        }}
      >
        This removes the budget for {yearMonth}.
      </ConfirmDialog>
    </div>
  );
};

/** One history row: its own mounted use_budget observer (Q3). */
const HistoryRow = ({ month }: { month: string }): JSX.Element => {
  const row = use_budget(month);
  const value =
    row.data === undefined ? EMPTY_HISTORY_PLACEHOLDER : row.data.amount === '0.00'
      ? EMPTY_HISTORY_PLACEHOLDER
      : row.data.amount;
  return (
    <li data-testid="budget-history-row" className="flex gap-3">
      <span>{month}</span>
      <span>{value}</span>
    </li>
  );
};

// BudgetForm — the set/edit upsert modal (REQ-FE-080/082, REQ-FE-111, t18).
//
// Budgets have no id, so create and edit are ONE form and ONE mutation
// (PUT by month via use_budget_mutations(ym).set — t18 Notes Q10). The
// modal mirrors t17's expense_form conventions verbatim: RHF + the
// hand-rolled zodResolver from utils/validation, mode:'onChange' (blur is
// a subset), backend {detail, code, field} errors mapped via applyApiErrors
// with an errors.root role="alert" line, values preserved on failure, reset
// on success, and focus moving into the first field on open then returning
// to the trigger on unmount (REQ-FE-111).
//
// Money never becomes a number: the amount travels as the decimal STRING
// the user typed (SetBudgetPayload.amount) and prefills from the query's
// amount string verbatim.

import { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import type { ApiError } from '../../api/client';
import { applyApiErrors, budgetFormSchema, zodResolver } from '../../utils/validation';
import type { BudgetFormValues } from '../../utils/validation';

export interface BudgetSubmitResult {
  ok: boolean;
  error?: ApiError;
}

interface BudgetFormProps {
  /** Existing amount string for this month ('0.00' when absent), or undefined. */
  currentAmount?: string;
  /** `YYYY-MM` label rendered in the heading (Builder-chosen copy, Q10). */
  yearMonth: string;
  onSubmit: (values: BudgetFormValues) => Promise<BudgetSubmitResult>;
  onCancel: () => void;
}

export const BudgetForm = ({
  currentAmount,
  yearMonth,
  onSubmit,
  onCancel
}: BudgetFormProps): JSX.Element => {
  const restoreRef = useRef<Element | null>(null);

  const {
    register: bindField,
    handleSubmit,
    setFocus,
    setError,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<BudgetFormValues>({
    resolver: zodResolver(budgetFormSchema),
    mode: 'onChange',
    defaultValues: { amount: currentAmount ?? '' }
  });

  useEffect(() => {
    restoreRef.current = document.activeElement;
    void setFocus('amount');
    return () => {
      const target = restoreRef.current;
      restoreRef.current = null;
      if (target instanceof HTMLElement) {
        target.focus();
      }
    };
  }, [setFocus]);

  const submit = async (values: BudgetFormValues): Promise<void> => {
    const result = await onSubmit(values);
    if (result.ok) {
      reset({ amount: '' });
      onCancel();
      return;
    }
    if (result.error) {
      applyApiErrors(result.error, (name, error) => {
        setError(name as keyof BudgetFormValues, error);
      });
    }
  };

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/50">
      <form
        role="dialog"
        aria-modal="true"
        aria-label="Set budget"
        className="w-full max-w-md rounded bg-white p-4 shadow"
        noValidate
        onSubmit={handleSubmit(submit)}
      >
        <h2 className="text-lg font-semibold text-slate-900">Set budget {yearMonth}</h2>
        <div className="mt-3 space-y-3">
          <div>
            <label className="block text-sm text-slate-700" htmlFor="budget-amount">
              Amount
            </label>
            <input
              className="w-full rounded border border-slate-300 p-2"
              id="budget-amount"
              inputMode="decimal"
              autoComplete="off"
              {...bindField('amount')}
            />
            {errors.amount ? (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            ) : null}
          </div>
          {errors.root ? (
            <p className="text-sm text-red-600" role="alert">
              {errors.root.message}
            </p>
          ) : null}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            className="rounded border border-slate-300 px-3 py-1"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="rounded bg-slate-800 px-3 py-1 text-white disabled:opacity-50"
            disabled={isSubmitting}
          >
            Save budget
          </button>
        </div>
      </form>
    </div>
  );
};

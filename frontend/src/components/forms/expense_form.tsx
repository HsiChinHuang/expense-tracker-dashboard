// ExpenseForm — create/edit modal (REQ-FE-081/082, REQ-FE-111, t17).
//
// RHF + the hand-rolled zodResolver from utils/validation (t9 helpers);
// validation runs onChange, which fires on blur AND on every keystroke
// after a field was touched (mode:'onChange' is a superset of onBlur).
// A backend {detail, code, field} error maps onto the named field via the
// merged applyApiErrors; values are preserved on failure and the form
// resets on success. Money never becomes a number: the amount travels as
// the decimal STRING the user typed (CreateExpensePayload.amount).
//
// Focus (REQ-FE-111): the first field receives focus on mount (open) and,
// when the modal unmounts (the parent closes it on success/cancel), focus
// returns to the element that was active before opening (the trigger).
//
// t73: the category control is a <select> of category NAMES fed by the
// merged use_categories query (the expenses_page filter select is the
// precedent markup), so a raw category UUID is never typed by hand. The
// payload still carries the selected row's category_id, and the zod
// min(1) leg in validation.ts is untouched — the select makes an invalid
// id unproducible. Pending/failed query states follow the merged t17
// inline role="status" / role="alert" + Retry conventions, and a list
// with no suitable category hints at the merged /categories page.

import { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import type { Expense } from '../../api/expenses';
import type { ApiError } from '../../api/client';
import { use_categories } from '../../hooks/use_categories';
import { applyApiErrors, expenseFormSchema, zodResolver } from '../../utils/validation';
import type { ExpenseFormValues } from '../../utils/validation';

export interface ExpenseSubmitResult {
  ok: boolean;
  error?: ApiError;
}

interface ExpenseFormProps {
  /** When provided the form edits this expense; otherwise it creates. */
  expense?: Expense;
  onSubmit: (values: ExpenseFormValues) => Promise<ExpenseSubmitResult>;
  onCancel: () => void;
}

const initialValues = (expense?: Expense): ExpenseFormValues => ({
  amount: expense?.amount ?? '',
  category_id: expense?.category_id ?? '',
  date: expense?.date ?? '',
  note: expense?.note ?? ''
});

export const ExpenseForm = ({ expense, onSubmit, onCancel }: ExpenseFormProps): JSX.Element => {
  const restoreRef = useRef<Element | null>(null);

  const {
    register: bindField,
    handleSubmit,
    setFocus,
    setError,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseFormSchema),
    mode: 'onChange',
    defaultValues: initialValues(expense)
  });

  const categories = use_categories();
  const categoryList = categories.data?.categories ?? [];
  // Controlled value: the option list arrives asynchronously, and a
  // controlled select reapplies the current value once the edited
  // expense's option renders (an uncontrolled one would drop to '').
  const categoryIdValue = watch('category_id');

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

  const submit = async (values: ExpenseFormValues): Promise<void> => {
    const result = await onSubmit(values);
    if (result.ok) {
      reset(initialValues());
      onCancel();
      return;
    }
    if (result.error) {
      applyApiErrors(result.error, (name, error) => {
        setError(name as keyof ExpenseFormValues, error);
      });
    }
  };

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/50">
      <form
        role="dialog"
        aria-modal="true"
        aria-label={expense ? 'Edit expense' : 'Add expense'}
        className="w-full max-w-md rounded bg-white p-4 shadow"
        noValidate
        onSubmit={handleSubmit(submit)}
      >
        <h2 className="text-lg font-semibold text-slate-900">
          {expense ? 'Edit expense' : 'Add expense'}
        </h2>
        <div className="mt-3 space-y-3">
          <div>
            <label className="block text-sm text-slate-700" htmlFor="expense-amount">
              Amount
            </label>
            <input
              className="w-full rounded border border-slate-300 p-2"
              id="expense-amount"
              inputMode="decimal"
              autoComplete="off"
              {...bindField('amount')}
            />
            {errors.amount ? (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            ) : null}
          </div>
          <div>
            <label className="block text-sm text-slate-700" htmlFor="expense-category">
              Category
            </label>
            {categories.isPending ? (
              <p role="status" className="text-sm text-slate-600">
                Loading categories…
              </p>
            ) : null}
            {categories.isError ? (
              <div role="alert" className="rounded bg-red-50 p-2 text-sm text-red-700">
                <p>Could not load categories.</p>
                <button
                  type="button"
                  className="mt-1 rounded border border-red-300 px-2 py-1"
                  onClick={() => {
                    void categories.refetch();
                  }}
                >
                  Retry
                </button>
              </div>
            ) : null}
            {!categories.isPending && !categories.isError ? (
              <>
                <select
                  className="w-full rounded border border-slate-300 bg-white p-2"
                  id="expense-category"
                  name="category_id"
                  value={categoryIdValue}
                  onChange={(event) => {
                    setValue('category_id', event.target.value, { shouldValidate: true });
                  }}
                >
                  <option value="">Select a category</option>
                  {categoryList.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                {categoryList.length === 0 ? (
                  <p className="mt-1 text-sm text-slate-600">
                    No suitable category? Add one on the Categories page (/categories) first.
                  </p>
                ) : null}
              </>
            ) : null}
            {errors.category_id ? (
              <p className="mt-1 text-sm text-red-600">{errors.category_id.message}</p>
            ) : null}
          </div>
          <div>
            <label className="block text-sm text-slate-700" htmlFor="expense-date">
              Date
            </label>
            <input
              className="w-full rounded border border-slate-300 p-2"
              id="expense-date"
              type="date"
              {...bindField('date')}
            />
            {errors.date ? <p className="mt-1 text-sm text-red-600">{errors.date.message}</p> : null}
          </div>
          <div>
            <label className="block text-sm text-slate-700" htmlFor="expense-note">
              Note
            </label>
            <textarea
              className="w-full rounded border border-slate-300 p-2"
              id="expense-note"
              rows={2}
              {...bindField('note')}
            />
            {errors.note ? (
              <p className="mt-1 text-sm text-red-600">{errors.note.message}</p>
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
            {expense ? 'Save changes' : 'Add expense'}
          </button>
        </div>
      </form>
    </div>
  );
};

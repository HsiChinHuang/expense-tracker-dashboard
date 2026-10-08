// ExpensesPage — the phase_3 expenses vertical slice (REQ-FE-063,
// REQ-FE-100/101/102, REQ-FE-015, t17).
//
// Data access goes through the merged t16 hooks ONLY (REQ-ARCH-012); no
// api/client.ts imports here. Month + category filters are page-local
// state feeding the year_month / category_id params (no MonthContext —
// phase_4 boundary); pagination is a page counter with the default page
// size 20. Money renders from the API string verbatim (REQ-PROD-023).
//
// The network-error path pays the t9 carry-forward: a list query whose
// request normalized to NETWORK_ERROR renders an offline error state with
// a Retry button (refetch), and a NETWORK_ERROR mutation failure raises a
// toast carrying the same retry callback (REQ-FE-033/102, REQ-PROD-036).

import { useEffect, useState } from 'react';
import { use_expense_mutations, use_expenses } from '../hooks/use_expenses';
import { use_categories } from '../hooks/use_categories';
import { ConfirmDialog } from '../components/ui/confirm_dialog';
import { ExpenseForm } from '../components/forms/expense_form';
import type { ExpenseSubmitResult } from '../components/forms/expense_form';
import { useToast } from '../context/toast_context';
import { NETWORK_ERROR_CODE, type ApiError } from '../api/client';
import type { Expense, ExpenseListParams, UpdateExpensePayload } from '../api/expenses';
import type { ExpenseFormValues } from '../utils/validation';

/** Page size requested by the pagination controls (REQ-FE-063: default 20). */
const PAGE_SIZE = 20;

interface FormState {
  mode: 'create' | 'edit';
  expense?: Expense;
}

export const ExpensesPage = (): JSX.Element => {
  const { showToast } = useToast();
  const [yearMonth, setYearMonth] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [page, setPage] = useState(1);

  const params: ExpenseListParams = {
    page,
    page_size: PAGE_SIZE,
    ...(yearMonth !== '' ? { year_month: yearMonth } : {}),
    ...(categoryId !== '' ? { category_id: categoryId } : {})
  };

  const list = use_expenses(params);
  const categories = use_categories();
  const { create, update, remove } = use_expense_mutations();

  const [form, setForm] = useState<FormState | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Expense | null>(null);

  // Unique page title (REQ-FE-015).
  useEffect(() => {
    document.title = 'Expenses';
  }, []);

  const notifyFailure = (error: ApiError): void => {
    if (error.code === NETWORK_ERROR_CODE) {
      showToast(error.message, 'error', {
        code: error.code,
        retry: () => {
          void list.refetch();
        }
      });
    } else {
      showToast(error.message, 'error');
    }
  };

  const submitForm = async (values: ExpenseFormValues): Promise<ExpenseSubmitResult> => {
    const payload = {
      amount: values.amount,
      category_id: values.category_id,
      date: values.date,
      ...(values.note !== undefined && values.note !== '' ? { note: values.note } : {})
    };
    try {
      if (form?.mode === 'edit' && form.expense) {
        const changed: UpdateExpensePayload = payload;
        await update.mutateAsync({ id: form.expense.id, payload: changed });
        showToast('Expense updated', 'success');
      } else {
        await create.mutateAsync(payload);
        showToast('Expense created', 'success');
      }
      return { ok: true };
    } catch (error) {
      const apiError = error as ApiError;
      notifyFailure(apiError);
      return { ok: false, error: apiError };
    }
  };

  const confirmDelete = async (): Promise<void> => {
    if (!pendingDelete) {
      return;
    }
    const target = pendingDelete;
    setPendingDelete(null);
    try {
      await remove.mutateAsync(target.id);
      showToast('Expense deleted', 'success');
    } catch (error) {
      notifyFailure(error as ApiError);
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Expenses</h1>
        <button
          type="button"
          className="rounded bg-slate-800 px-3 py-1 text-white"
          onClick={() => {
            setForm({ mode: 'create' });
          }}
        >
          Add expense
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <label className="text-sm text-slate-700">
          Month
          <input
            aria-label="Month filter"
            type="month"
            className="ml-2 rounded border border-slate-300 p-1"
            value={yearMonth}
            onChange={(event) => {
              setYearMonth(event.target.value);
              setPage(1);
            }}
          />
        </label>
        <label className="text-sm text-slate-700">
          Category
          <select
            aria-label="Category filter"
            className="ml-2 rounded border border-slate-300 p-1"
            value={categoryId}
            onChange={(event) => {
              setCategoryId(event.target.value);
              setPage(1);
            }}
          >
            <option value="">All categories</option>
            {(categories.data?.categories ?? []).map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {list.isPending ? (
        <p role="status" className="mt-4 text-slate-600">
          Loading expenses…
        </p>
      ) : null}

      {list.isError ? (
        <div role="alert" className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">
          <p>Could not load expenses. The server may be unreachable.</p>
          <button
            type="button"
            className="mt-2 rounded border border-red-300 px-2 py-1"
            onClick={() => {
              void list.refetch();
            }}
          >
            Retry
          </button>
        </div>
      ) : null}

      {!list.isPending && !list.isError && list.data && list.data.items.length === 0 ? (
        <p className="mt-4 text-slate-600">No expenses yet. Add your first expense.</p>
      ) : null}

      {!list.isPending && !list.isError && list.data && list.data.items.length > 0 ? (
        <>
          <table className="mt-4 w-full border-collapse text-left text-sm">
            <thead>
              <tr>
                <th className="border-b border-slate-200 py-2">Date</th>
                <th className="border-b border-slate-200 py-2">Category</th>
                <th className="border-b border-slate-200 py-2">Amount</th>
                <th className="border-b border-slate-200 py-2">Note</th>
                <th className="border-b border-slate-200 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {list.data.items.map((expense) => (
                <tr key={expense.id}>
                  <td className="py-2">{expense.date}</td>
                  <td className="py-2">{expense.category_name}</td>
                  <td className="py-2">{expense.amount}</td>
                  <td className="py-2">{expense.note ?? ''}</td>
                  <td className="py-2">
                    <button
                      type="button"
                      className="mr-2 underline"
                      onClick={() => {
                        setForm({ mode: 'edit', expense });
                      }}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="underline text-red-700"
                      onClick={() => {
                        setPendingDelete(expense);
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-3 flex items-center gap-2 text-sm">
            <button
              type="button"
              className="rounded border border-slate-300 px-2 py-1 disabled:opacity-50"
              disabled={page <= 1}
              onClick={() => {
                setPage((current) => Math.max(1, current - 1));
              }}
            >
              Previous page
            </button>
            <span aria-label="Current page">Page {list.data.page}</span>
            <button
              type="button"
              className="rounded border border-slate-300 px-2 py-1"
              onClick={() => {
                setPage((current) => current + 1);
              }}
            >
              Next page
            </button>
          </div>
        </>
      ) : null}

      {form ? (
        <ExpenseForm
          {...(form.expense ? { expense: form.expense } : {})}
          onSubmit={submitForm}
          onCancel={() => {
            setForm(null);
          }}
        />
      ) : null}

      <ConfirmDialog
        open={pendingDelete !== null}
        title="Delete expense"
        onConfirm={() => {
          void confirmDelete();
        }}
        onCancel={() => {
          setPendingDelete(null);
        }}
      >
        This removes the expense permanently.
      </ConfirmDialog>
    </div>
  );
};

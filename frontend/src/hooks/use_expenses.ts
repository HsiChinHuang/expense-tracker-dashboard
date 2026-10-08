/* eslint-disable react-hooks/rules-of-hooks -- the project coding standard
pins snake_case hook names (use_expenses); eslint-plugin-react-hooks only
recognizes usePascalCase, so the recognition false-positive is scoped off
here while the Rules of Hooks are still followed by construction. */
// Expense data hooks (REQ-FE-034/035, REQ-FE-051, t16).
//
// Server state is owned by TanStack Query; the hooks call ONLY the typed
// functions in `src/api/expenses.ts` through the queryKeys factory. The
// mutation hooks implement the REQ-FE-051 invalidation matrix: every
// expense create/update/delete invalidates the ["expenses"] family AND
// the ["dashboard"] prefix (a phase_4 key — invalidating it now is
// intentional and observable via a mounted dashboard-prefixed observer).

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createExpense,
  deleteExpense,
  getExpense,
  listExpenses,
  updateExpense,
  type CreateExpensePayload,
  type ExpenseListParams,
  type UpdateExpensePayload
} from '../api/expenses';
import { queryKeys } from '../api/query_keys';

/** List query backed by the paginated envelope endpoint. */
export const use_expenses = (params?: ExpenseListParams) =>
  useQuery({
    queryKey: queryKeys.expenses.list(params),
    queryFn: () => listExpenses(params)
  });

/** Single-expense query keyed under the same ["expenses"] family. */
export const use_expense_detail = (id: string) =>
  useQuery({
    queryKey: queryKeys.expenses.detail(id),
    queryFn: () => getExpense(id)
  });

/**
 * Create/update/delete mutations. On success each invalidates
 * ["expenses"] and ["dashboard"] (REQ-FE-051) — never ["categories"]
 * or ["budgets"].
 */
export const use_expense_mutations = () => {
  const queryClient = useQueryClient();

  const invalidate = async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.expenses.root }),
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    ]);
  };

  const create = useMutation({
    mutationFn: (payload: CreateExpensePayload) => createExpense(payload),
    onSuccess: invalidate
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateExpensePayload }) =>
      updateExpense(id, payload),
    onSuccess: invalidate
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteExpense(id),
    onSuccess: invalidate
  });

  return { create, update, remove };
};

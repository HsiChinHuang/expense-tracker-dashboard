/* eslint-disable react-hooks/rules-of-hooks -- the project coding standard
pins snake_case hook names (use_budget); eslint-plugin-react-hooks only
recognizes usePascalCase, so the recognition false-positive is scoped off
here while the Rules of Hooks are still followed by construction. */
// Budget data hooks (REQ-FE-034/035, REQ-FE-051, t16).
//
// use_budget reads one month through api/budgets.getBudget (absent months
// resolve to the string "0.00" — no number coercion anywhere). The
// mutation hooks invalidate ["budgets"] plus the ["dashboard"] prefix per
// REQ-FE-051; they never touch ["expenses"] or ["categories"].

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { deleteBudget, getBudget, setBudget } from '../api/budgets';
import { queryKeys } from '../api/query_keys';

/** One month's budget keyed under the ["budgets"] family. */
export const use_budget = (yearMonth: string) =>
  useQuery({
    queryKey: queryKeys.budgets.byMonth(yearMonth),
    queryFn: () => getBudget(yearMonth)
  });

/**
 * Upsert/delete mutations. On success each invalidates ["budgets"] and
 * ["dashboard"] (REQ-FE-051).
 */
export const use_budget_mutations = (yearMonth: string) => {
  const queryClient = useQueryClient();

  const invalidate = async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.budgets.root }),
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    ]);
  };

  const set = useMutation({
    mutationFn: (amount: string) => setBudget(yearMonth, { amount }),
    onSuccess: invalidate
  });

  const remove = useMutation({
    mutationFn: () => deleteBudget(yearMonth),
    onSuccess: invalidate
  });

  return { set, remove };
};

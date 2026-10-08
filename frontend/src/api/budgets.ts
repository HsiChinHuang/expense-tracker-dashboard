// Typed budget API module (REQ-FE-042/043, t14 contract mirror).
//
// One function per Chapter 7 §7.6 endpoint, 1:1, through the shared `api`
// instance (REQ-ARCH-070). The amount is the frozen 2-decimal STRING —
// including the absent-month `"0.00"` synthesis — and this module performs
// no numeric coercion (REQ-SEC-050 / REQ-PROD-023).

import { api } from './client';

/** Public budget representation — exactly the two backend fields (REQ-API-050). */
export interface Budget {
  /** `YYYY-MM` path echo. */
  year_month: string;
  /** 2-decimal string such as "2000.00"; "0.00" for an absent month. */
  amount: string;
}

/** Payload for PUT /api/v1/budgets/{year_month} (upsert). */
export interface SetBudgetPayload {
  /** Decimal string such as "2000.00" — kept as a string (REQ-PROD-023). */
  amount: string;
}

/** Fetch one month's budget (absent well-formed month -> amount "0.00"). */
export const getBudget = async (yearMonth: string): Promise<Budget> => {
  const response = await api.get<Budget>(`/api/v1/budgets/${yearMonth}`);
  return response.data;
};

/** Upsert one month's budget (200 for both create and update). */
export const setBudget = async (
  yearMonth: string,
  payload: SetBudgetPayload
): Promise<Budget> => {
  const response = await api.put<Budget>(`/api/v1/budgets/${yearMonth}`, payload);
  return response.data;
};

/** Delete one month's budget. */
export const deleteBudget = async (yearMonth: string): Promise<void> => {
  await api.delete(`/api/v1/budgets/${yearMonth}`);
};

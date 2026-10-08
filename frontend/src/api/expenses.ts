// Typed expense API module (REQ-FE-042/043, t13 contract mirror).
//
// One function per Chapter 7 §7.5 endpoint, 1:1, through the shared `api`
// instance (REQ-ARCH-070). Money is the frozen 2-decimal STRING on every
// type (REQ-SEC-050 frontend half / REQ-PROD-023): this module never
// converts amounts to numbers. Dates are plain `YYYY-MM-DD` strings and
// timestamps ISO strings.

import { api } from './client';

/** Public expense representation — exactly the ten backend fields (REQ-API-040). */
export interface Expense {
  id: string;
  /** 2-decimal string such as "125.50" — never a number (REQ-SEC-050). */
  amount: string;
  currency: string;
  category_id: string;
  category_name: string;
  category_color: string;
  /** Calendar date, `YYYY-MM-DD`, no timezone (REQ-SEC-051). */
  date: string;
  note: string | null;
  created_at: string;
  updated_at: string;
}

/** The frozen four-key W6 pagination envelope (Chapter 7 §7.5.1). */
export interface ExpenseList {
  items: Expense[];
  total: number;
  page: number;
  page_size: number;
}

/** Query filters for GET /api/v1/expenses. */
export interface ExpenseListParams {
  /** `YYYY-MM` month filter. */
  year_month?: string;
  category_id?: string;
  page?: number;
  page_size?: number;
}

/** Payload for POST /api/v1/expenses (currency is not a client field). */
export interface CreateExpensePayload {
  /** Decimal string such as "42.50" — kept as a string (REQ-PROD-023). */
  amount: string;
  category_id: string;
  /** `YYYY-MM-DD` calendar date. */
  date: string;
  note?: string;
}

/** Payload for PUT /api/v1/expenses/{id} — at least one field required. */
export interface UpdateExpensePayload {
  amount?: string;
  category_id?: string;
  date?: string;
  note?: string | null;
}

/** List expenses with filters/pagination; only defined params are sent. */
export const listExpenses = async (
  params?: ExpenseListParams
): Promise<ExpenseList> => {
  const search = new URLSearchParams();
  if (params) {
    for (const key of ['year_month', 'category_id', 'page', 'page_size'] as const) {
      const value = params[key];
      if (value !== undefined) {
        search.set(key, String(value));
      }
    }
  }
  const query = search.toString();
  const response = await api.get<ExpenseList>(
    query ? `/api/v1/expenses?${query}` : '/api/v1/expenses'
  );
  return response.data;
};

/** Create one expense. */
export const createExpense = async (
  payload: CreateExpensePayload
): Promise<Expense> => {
  const response = await api.post<Expense>('/api/v1/expenses', payload);
  return response.data;
};

/** Fetch a single expense by id. */
export const getExpense = async (id: string): Promise<Expense> => {
  const response = await api.get<Expense>(`/api/v1/expenses/${id}`);
  return response.data;
};

/** Partially update one expense (at least one field). */
export const updateExpense = async (
  id: string,
  payload: UpdateExpensePayload
): Promise<Expense> => {
  const response = await api.put<Expense>(`/api/v1/expenses/${id}`, payload);
  return response.data;
};

/** Delete one expense. */
export const deleteExpense = async (id: string): Promise<void> => {
  await api.delete(`/api/v1/expenses/${id}`);
};

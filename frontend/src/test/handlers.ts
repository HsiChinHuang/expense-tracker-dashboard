// MSW handlers for the auth + phase_3 endpoints (REQ-FE-133 / REQ-TEST-039).
//
// Fixtures mirror the merged backend contracts exactly: the t8 auth trio,
// plus the t11 categories (object-wrapper list), t13 expenses (four-key
// pagination envelope, 2-decimal string amounts) and t14 budgets (absent
// month -> 200 {year_month, amount: "0.00"}). Error bodies use the backend
// shape {detail, code, field}.
//
// Every phase_3 handler also bumps a shared in-memory call counter so the
// ac3 invalidation tests can OBSERVE refetch traffic as call-count deltas
// instead of reading hook code (docs/issues/t16.md ## Notes).

import { http, HttpResponse } from 'msw';
import type { LoginResult, User } from '../api/auth';
import type { Budget } from '../api/budgets';
import type { Category, CategoryList } from '../api/categories';
import type { Expense, ExpenseList } from '../api/expenses';

export const TEST_TOKEN = 'test-token-abc';

export const demoUser: User = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  email: 'demo@example.com',
  username: 'demo',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z'
};

export const authHandlers = [
  // Full literal endpoint paths (api/v1/auth/login, api/v1/auth/register,
  // api/v1/auth/me) so the AC5 grep sees the contract paths verbatim.
  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = (await request.json()) as { email?: string; password?: string };
    if (body.email === demoUser.email && body.password === 'correct-horse') {
      const result: LoginResult = {
        access_token: TEST_TOKEN,
        token_type: 'bearer',
        user: demoUser
      };
      return HttpResponse.json(result, { status: 200 });
    }
    return HttpResponse.json(
      { detail: 'Incorrect email or password', code: 'INVALID_CREDENTIALS', field: null },
      { status: 401 }
    );
  }),

  http.post('/api/v1/auth/register', async ({ request }) => {
    const body = (await request.json()) as { email?: string; username?: string };
    if (body.email === 'taken@example.com') {
      return HttpResponse.json(
        { detail: 'email already registered', code: 'DUPLICATE_EMAIL', field: 'email' },
        { status: 409 }
      );
    }
    const user: User = {
      ...demoUser,
      email: body.email ?? demoUser.email,
      username: body.username ?? demoUser.username
    };
    const result: LoginResult = {
      access_token: TEST_TOKEN,
      token_type: 'bearer',
      user
    };
    return HttpResponse.json(result, { status: 201 });
  }),

  http.get('/api/v1/auth/me', ({ request }) => {
    const auth = request.headers.get('Authorization');
    if (auth === `Bearer ${TEST_TOKEN}`) {
      return HttpResponse.json(demoUser, { status: 200 });
    }
    return HttpResponse.json(
      { detail: 'invalid or expired token', code: 'TOKEN_INVALID', field: null },
      { status: 401 }
    );
  })
];

// ---------------------------------------------------------------------------
// phase_3 fixtures + counted handlers (t11/t13/t14 contract mirrors)
// ---------------------------------------------------------------------------

/** In-memory call counter per phase_3 handler, keyed by handler name. */
export const callCounts: Record<string, number> = {};

/** Zero every phase_3 handler counter (call from test setup). */
export const resetCallCounts = (): void => {
  for (const key of Object.keys(callCounts)) {
    delete callCounts[key];
  }
};

/** Bump and return the counter for one handler. */
const count = (name: string): number => {
  const next = (callCounts[name] ?? 0) + 1;
  callCounts[name] = next;
  return next;
};

/** Read a counter without creating it. */
export const callCount = (name: string): number => callCounts[name] ?? 0;

export const demoCategory: Category = {
  id: 'c1000000-0000-4000-8000-000000000001',
  name: 'Food',
  color: '#EF4444',
  icon: 'utensils',
  is_system: true,
  created_at: '2026-01-01T00:00:00Z'
};

export const demoExpense: Expense = {
  id: 'e1000000-0000-4000-8000-000000000001',
  amount: '125.50',
  currency: 'USD',
  category_id: demoCategory.id,
  category_name: demoCategory.name,
  category_color: demoCategory.color,
  date: '2026-02-03',
  note: 'groceries',
  created_at: '2026-02-03T09:00:00Z',
  updated_at: '2026-02-03T09:00:00Z'
};

export const demoBudget: Budget = {
  year_month: '2026-02',
  amount: '2000.00'
};

/** Counted dummy endpoint backing the ["dashboard", "probe"] observer (ac3). */
export const DASHBOARD_PROBE_PATH = '/api/v1/dashboard/probe';

export const phase3Handlers = [
  // --- categories (t11): object-wrapper list, 201 create, 204 delete ---
  http.get('/api/v1/categories', () => {
    count('categories.list');
    const body: CategoryList = { categories: [demoCategory] };
    return HttpResponse.json(body, { status: 200 });
  }),

  http.post('/api/v1/categories', async ({ request }) => {
    count('categories.create');
    const body = (await request.json()) as {
      name?: string;
      color?: string;
      icon?: string | null;
    };
    const created: Category = {
      ...demoCategory,
      id: 'c2000000-0000-4000-8000-000000000002',
      name: body.name ?? 'Custom',
      color: body.color ?? demoCategory.color,
      icon: typeof body.icon === 'string' ? body.icon : null,
      is_system: false
    };
    return HttpResponse.json(created, { status: 201 });
  }),

  http.delete('/api/v1/categories/:id', () => {
    count('categories.delete');
    return new HttpResponse(null, { status: 204 });
  }),

  // --- expenses (t13): four-key envelope, 201 create, detail/update 200, 204 delete ---
  http.get('/api/v1/expenses', ({ request }) => {
    count('expenses.list');
    const url = new URL(request.url);
    const pageParam = url.searchParams.get('page');
    const sizeParam = url.searchParams.get('page_size');
    const body: ExpenseList = {
      items: [demoExpense],
      total: 1,
      page: pageParam !== null && pageParam !== '' ? Number(pageParam) : 1,
      page_size: sizeParam !== null && sizeParam !== '' ? Number(sizeParam) : 20
    };
    return HttpResponse.json(body, { status: 200 });
  }),

  http.post('/api/v1/expenses', async ({ request }) => {
    count('expenses.create');
    const body = (await request.json()) as {
      amount?: string;
      category_id?: string;
      date?: string;
      note?: string | null;
    };
    const created: Expense = {
      ...demoExpense,
      id: 'e2000000-0000-4000-8000-000000000002',
      amount: body.amount ?? demoExpense.amount,
      category_id: body.category_id ?? demoExpense.category_id,
      date: body.date ?? demoExpense.date,
      note: typeof body.note === 'string' ? body.note : null
    };
    return HttpResponse.json(created, { status: 201 });
  }),

  http.get('/api/v1/expenses/:id', ({ params }) => {
    count('expenses.detail');
    const detail: Expense = { ...demoExpense, id: String(params.id) };
    return HttpResponse.json(detail, { status: 200 });
  }),

  http.put('/api/v1/expenses/:id', async ({ request, params }) => {
    count('expenses.update');
    const body = (await request.json()) as {
      amount?: string;
      category_id?: string;
      date?: string;
      note?: string | null;
    };
    const updated: Expense = {
      ...demoExpense,
      id: String(params.id),
      amount: body.amount ?? demoExpense.amount,
      category_id: body.category_id ?? demoExpense.category_id,
      date: body.date ?? demoExpense.date,
      note: typeof body.note === 'string' ? body.note : null
    };
    return HttpResponse.json(updated, { status: 200 });
  }),

  http.delete('/api/v1/expenses/:id', () => {
    count('expenses.delete');
    return new HttpResponse(null, { status: 204 });
  }),

  // --- budgets (t14): absent month -> 200 "0.00", PUT upsert 200, DELETE 204 ---
  http.get('/api/v1/budgets/:year_month', ({ params }) => {
    count('budgets.get');
    const ym = String(params.year_month);
    const body: Budget =
      ym === demoBudget.year_month ? demoBudget : { year_month: ym, amount: '0.00' };
    return HttpResponse.json(body, { status: 200 });
  }),

  http.put('/api/v1/budgets/:year_month', async ({ request, params }) => {
    count('budgets.set');
    const body = (await request.json()) as { amount?: string };
    const saved: Budget = {
      year_month: String(params.year_month),
      amount: body.amount ?? '0.00'
    };
    return HttpResponse.json(saved, { status: 200 });
  }),

  http.delete('/api/v1/budgets/:year_month', () => {
    count('budgets.delete');
    return new HttpResponse(null, { status: 204 });
  }),

  // --- dashboard probe (ac3 dummy observer target; not a real endpoint) ---
  http.get(DASHBOARD_PROBE_PATH, () => {
    count('dashboard.probe');
    return HttpResponse.json({ ok: true }, { status: 200 });
  })
];

export const handlers = [...authHandlers, ...phase3Handlers];

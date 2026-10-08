// AC4: MSW handler contract tests (REQ-FE-133).
//
// Proves the phase_3 handlers mirror the merged server contract: all 11
// endpoints resolve through the typed api modules against the shared
// handlers, the budgets-absent body carries the string "0.00", the
// expenses list body is the frozen four-key envelope, and an unhandled
// request fails loudly through the onUnhandledRequest 'error' harness.

import { describe, expect, it } from 'vitest';
import { listCategories, createCategory, deleteCategory } from '../api/categories';
import {
  listExpenses,
  createExpense,
  getExpense,
  updateExpense,
  deleteExpense
} from '../api/expenses';
import { getBudget, setBudget, deleteBudget } from '../api/budgets';
import { demoBudget, demoCategory, demoExpense } from './handlers';
import { api } from '../api/client';

describe('phase_3 MSW handler contract', () => {
  it('the three api modules resolve against the MSW handlers for all eleven phase_3 endpoints', async () => {
    // categories (3)
    const list = await listCategories();
    expect(list.categories[0]?.id).toBe(demoCategory.id);
    const created = await createCategory({ name: 'Custom', color: '#123456', icon: 'star' });
    expect(created.name).toBe('Custom');
    expect(created.is_system).toBe(false);
    await expect(deleteCategory(demoCategory.id)).resolves.toBeUndefined();

    // expenses (5)
    const page = await listExpenses({ year_month: '2026-02', page: 1, page_size: 10 });
    expect(page.items[0]?.id).toBe(demoExpense.id);
    const expense = await createExpense({
      amount: '42.50',
      category_id: demoCategory.id,
      date: '2026-02-05'
    });
    expect(expense.amount).toBe('42.50');
    const one = await getExpense(demoExpense.id);
    expect(one.id).toBe(demoExpense.id);
    const updated = await updateExpense(demoExpense.id, { amount: '99.99' });
    expect(updated.amount).toBe('99.99');
    await expect(deleteExpense(demoExpense.id)).resolves.toBeUndefined();

    // budgets (3)
    const budget = await getBudget('2026-02');
    expect(budget.amount).toBe('2000.00');
    const saved = await setBudget('2026-03', { amount: '1500.00' });
    expect(saved).toEqual({ year_month: '2026-03', amount: '1500.00' });
    await expect(deleteBudget('2026-03')).resolves.toBeUndefined();
  });

  it('the budget handler returns the absent month as the string 0.00', async () => {
    const absent = await getBudget('2031-12');
    expect(absent).toEqual({ year_month: '2031-12', amount: '0.00' });
    expect(typeof absent.amount).toBe('string');
    // The stored-month fixture is a string too (no float ever surfaces).
    expect(typeof demoBudget.amount).toBe('string');
  });

  it('the expenses handler returns the four-key pagination envelope', async () => {
    const raw = await api.get<Record<string, unknown>>('/api/v1/expenses?page=2&page_size=5');
    expect(Object.keys(raw.data).sort()).toEqual(['items', 'page', 'page_size', 'total']);
    expect(raw.data.page).toBe(2);
    expect(raw.data.page_size).toBe(5);
    expect(raw.data.total).toBe(1);
    const envelope = await listExpenses({ page: 2, page_size: 5 });
    expect(envelope.items[0]?.amount).toBe('125.50');
  });

  it('an unhandled request fails loudly through the error onUnhandledRequest harness', async () => {
    // No handler exists for this path: the t9 harness (listen with
    // onUnhandledRequest: 'error') errors the request instead of proxying
    // it, so the call must reject loudly rather than resolve.
    let rejected = false;
    try {
      await api.get('/api/v1/nonexistent-endpoint');
    } catch (error) {
      rejected = true;
      const message = error instanceof Error ? error.message : JSON.stringify(error);
      expect(message.length).toBeGreaterThan(0);
    }
    expect(rejected).toBe(true);
  });
});

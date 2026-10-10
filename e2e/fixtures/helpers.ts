// Step helpers (REQ-TEST-041) - the four UI flows the specs compose.
//
// Every helper drives MERGED markup ONLY (t27 selector contract): roles,
// labels and the data-testid values that already exist in merged
// components (kpi-total, kpi-budget, kpi-remaining, kpi-categories,
// recent-item, month-picker-label). NO new product selector may be added
// for these specs - getByRole / getByLabel are the primary locators and
// getByTestId is reserved for the merged test ids above.
//
// Month strings are built with UTC getters (currentMonth / previousMonth)
// so the seeded dates match the month the dashboard's MonthPicker shows.

import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';
import type { UniqueUser } from './users';

/** Register through /register (labelled Email / Username / Password fields). */
export const registerUser = async (page: Page, user: UniqueUser): Promise<void> => {
  await test.step('registerUser', async () => {
    await page.goto('/register');
    await page.getByLabel('Email').fill(user.email);
    await page.getByLabel('Username').fill(user.username);
    await page.getByLabel('Password').fill(user.password);
    await page.getByLabel('Confirm password').fill(user.password);
    await page.getByRole('button', { name: 'Register' }).click();
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
};

/** Log in through /login and land on the dashboard. */
export const loginUser = async (page: Page, user: UniqueUser): Promise<void> => {
  await test.step('loginUser', async () => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(user.email);
    await page.getByLabel('Password').fill(user.password);
    await page.getByRole('button', { name: 'Log in' }).click();
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
};

/** YYYY-MM of the current month (UTC), e.g. "2026-10". */
export const currentMonth = (): string => {
  const now = new Date();
  const year = now.getUTCFullYear();
  const month = String(now.getUTCMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
};

/** YYYY-MM of the previous month (UTC), e.g. "2026-09". */
export const previousMonth = (): string => {
  const now = new Date();
  const prev = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - 1, 1));
  const year = prev.getUTCFullYear();
  const month = String(prev.getUTCMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
};

/** YYYY-MM-DD inside a given YYYY-MM month (day clamped into the month). */
export const dayInMonth = (yearMonth: string, day: number): string => {
  const [year, month] = yearMonth.split('-').map((part) => Number.parseInt(part, 10));
  const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const clamped = Math.min(Math.max(day, 1), lastDay);
  return `${yearMonth}-${String(clamped).padStart(2, '0')}`;
};

/**
 * Add one expense through the /expenses "Add expense" dialog. The category
 * is resolved by name from the merged /categories page (system categories
 * carry no id in the UI, and the dialog takes the raw id text).
 */
export const addExpense = async (
  page: Page,
  options: { amount: string; categoryName: string; date: string; note?: string }
): Promise<void> => {
  await test.step('addExpense', async () => {
    const categoryId = await resolveCategoryId(page, options.categoryName);
    await page.goto('/expenses');
    await page.getByRole('button', { name: 'Add expense' }).click();
    const dialog = page.getByRole('dialog', { name: 'Add expense' });
    await dialog.getByLabel('Amount').fill(options.amount);
    await dialog.getByLabel('Category id').fill(categoryId);
    await dialog.getByLabel('Date').fill(options.date);
    if (options.note !== undefined) {
      await dialog.getByLabel('Note').fill(options.note);
    }
    await dialog.getByRole('button', { name: 'Add expense' }).click();
    await expect(
      page.getByRole('heading', { name: 'Expenses' })
    ).toBeVisible();
  });
};

/** Set this month's budget through the /budgets page form. */
export const setBudget = async (page: Page, amount: string): Promise<void> => {
  await test.step('setBudget', async () => {
    await page.goto('/budgets');
    await page.getByRole('button', { name: 'Set budget' }).click();
    const form = page.getByRole('dialog', { name: 'Set budget' });
    await form.getByLabel('Amount').fill(amount);
    await form.getByRole('button', { name: 'Save budget' }).click();
    await expect(page.getByRole('heading', { name: 'Budget' })).toBeVisible();
  });
};

/** Edit the newest expense row: open its Edit dialog, save new amount. */
export const editFirstExpense = async (page: Page, amount: string): Promise<void> => {
  await test.step('editFirstExpense', async () => {
    await page.goto('/expenses');
    await page.getByRole('button', { name: 'Edit' }).first().click();
    const dialog = page.getByRole('dialog', { name: 'Edit expense' });
    await dialog.getByLabel('Amount').fill(amount);
    await dialog.getByRole('button', { name: 'Save changes' }).click();
    await expect(page.getByRole('heading', { name: 'Expenses' })).toBeVisible();
  });
};

/** Delete the newest expense row through the Delete expense confirm dialog. */
export const deleteFirstExpense = async (page: Page): Promise<void> => {
  await test.step('deleteFirstExpense', async () => {
    await page.goto('/expenses');
    await page.getByRole('button', { name: 'Delete' }).first().click();
    const dialog = page.getByRole('dialog', { name: 'Delete expense' });
    await dialog.getByRole('button', { name: 'Confirm' }).click();
    await expect(page.getByRole('heading', { name: 'Expenses' })).toBeVisible();
  });
};

/** Log out from the dashboard header. */
export const logout = async (page: Page): Promise<void> => {
  await test.step('logout', async () => {
    await page.getByRole('button', { name: 'Log out' }).click();
  });
};

/**
 * The five chart surfaces (REQ-TEST-042), pinned from merged aria-labels /
 * roles: pie, trend bar, cumulative line, weekly heatmap grid, budget
 * progressbar. The specs assert all five by these exact names.
 */
export const chartSurfaces = [
  'Spending by category pie chart',
  'Monthly spending trend bar chart',
  'Cumulative spending line chart',
  'Weekly spending heatmap grid',
  'Budget usage'
] as const;

/**
 * Resolve a category id by name. The merged UI renders system rows without
 * their ids (the /categories list shows name + color only), so the id is
 * read from the same GET /api/v1/categories response the page consumes -
 * the API base the frontend itself is configured against (E2E_API_URL).
 */
const resolveCategoryId = async (page: Page, categoryName: string): Promise<string> => {
  const front = process.env.E2E_BASE_URL ?? 'http://localhost:5173';
  const apiBase =
    process.env.E2E_API_URL ?? `${new URL(front).origin}/api/v1`;
  const token = await page.evaluate(() => window.localStorage.getItem('token'));
  const response = await page.requestGet(`${apiBase}/categories`, {
    headers: token === null ? {} : { Authorization: `Bearer ${token}` }
  });
  const body = (await response.json()) as { categories: { id: string; name: string }[] };
  const match = body.categories.find((category) => category.name === categoryName);
  if (match === undefined) {
    throw new Error(`category not found: ${categoryName}`);
  }
  return match.id;
};

// Happy-path E2E spec (REQ-TEST-042).
//
// One registered user, one month: register -> three expenses -> budget ->
// dashboard totals -> five charts -> three recent rows -> edit -> verify ->
// delete -> verify -> logout -> re-login. The user comes from uniqueUser
// (REQ-TEST-045) so this run is isolated from every other test; the suite
// performs NO teardown of any kind (REQ-TEST-045 leaves the data behind).

import { expect, test } from '@playwright/test';
import {
  addExpense,
  chartSurfaces,
  currentMonth,
  dayInMonth,
  deleteFirstExpense,
  editFirstExpense,
  loginUser,
  logout,
  registerUser,
  setBudget
} from '../fixtures/helpers';
import { uniqueUser } from '../fixtures/users';

const CATEGORY = 'Food';

test('happy path: register, spend, budget, verify, edit, delete, logout, re-login', async ({
  page
}) => {
  const user = uniqueUser();
  const month = currentMonth();

  await registerUser(page, user);

  await addExpense(page, { amount: '12.50', categoryName: CATEGORY, date: dayInMonth(month, 3), note: 'lunch' });
  await addExpense(page, { amount: '30.00', categoryName: CATEGORY, date: dayInMonth(month, 5), note: 'groceries' });
  await addExpense(page, { amount: '7.25', categoryName: CATEGORY, date: dayInMonth(month, 8), note: 'coffee' });

  await setBudget(page, '500.00');

  await page.goto('/');
  await expect(page.getByTestId('kpi-total')).toHaveText('$59.75');
  await expect(page.getByTestId('kpi-budget')).toHaveText('$500.00');
  await expect(page.getByTestId('kpi-remaining')).toHaveText('$440.25');
  await expect(page.getByTestId('kpi-categories')).toHaveText('1');

  for (const surface of chartSurfaces) {
    await expect(page.getByRole('img', { name: surface })).toBeVisible();
  }
  await expect(page.getByRole('progressbar', { name: 'Budget usage' })).toBeVisible();

  await expect(page.getByTestId('recent-item')).toHaveCount(3);

  await editFirstExpense(page, '22.50');
  await page.goto('/');
  await expect(page.getByTestId('kpi-total')).toHaveText('$69.75');
  await expect(page.getByTestId('recent-item')).toHaveCount(3);

  await deleteFirstExpense(page);
  await page.goto('/');
  await expect(page.getByTestId('recent-item')).toHaveCount(2);
  await expect(page.getByTestId('kpi-total')).toHaveText('$42.50');

  await logout(page);
  await loginUser(page, user);
  await expect(page.getByTestId('kpi-total')).toHaveText('$42.50');
});

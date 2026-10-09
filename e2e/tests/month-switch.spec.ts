// Month-switch E2E spec (REQ-TEST-044).
//
// One unique user, two months: one expense in currentMonth and one in
// previousMonth. The dashboard opens on the current month, so the total
// shows only that expense; stepping "Previous month" must show the other
// total, and stepping "Next month" must restore it. No cleanup hooks.

import { expect, test } from '@playwright/test';
import {
  addExpense,
  currentMonth,
  dayInMonth,
  loginUser,
  previousMonth,
  registerUser
} from '../fixtures/helpers';
import { uniqueUser } from '../fixtures/users';

test('switching months updates the dashboard totals', async ({ page }) => {
  const user = uniqueUser();
  const thisMonth = currentMonth();
  const lastMonth = previousMonth();

  await registerUser(page, user);

  await addExpense(page, {
    amount: '40.00',
    categoryName: 'Food',
    date: dayInMonth(thisMonth, 6),
    note: 'this month'
  });
  await addExpense(page, {
    amount: '25.00',
    categoryName: 'Transport',
    date: dayInMonth(lastMonth, 12),
    note: 'last month'
  });

  await page.goto('/');
  await expect(page.getByTestId('kpi-total')).toHaveText('$40.00');

  await page.getByRole('button', { name: 'Previous month' }).click();
  await expect(page.getByTestId('kpi-total')).toHaveText('$25.00');

  await page.getByRole('button', { name: 'Next month' }).click();
  await expect(page.getByTestId('kpi-total')).toHaveText('$40.00');

  // A reload keeps the session and the current-month total (smoke).
  await loginUser(page, user);
  await expect(page.getByTestId('kpi-total')).toHaveText('$40.00');
});

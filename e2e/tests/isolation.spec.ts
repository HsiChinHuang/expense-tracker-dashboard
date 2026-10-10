// Per-user isolation E2E spec (REQ-TEST-043).
//
// Two independent browser contexts, two unique users. User A records an
// expense; User B - a freshly registered account in the second context -
// must see an untouched dashboard: $0.00 total, zero recent rows and the
// merged "No recent transactions" empty state. Each context closes itself
// inside the test body; there is NO shared-fixture teardown anywhere
// (REQ-TEST-045).

import { expect, test } from '@playwright/test';
import { addExpense, currentMonth, dayInMonth, registerUser } from '../fixtures/helpers';
import { uniqueUser } from '../fixtures/users';

test('two users see only their own data', async ({ browser }) => {
  const userA = uniqueUser();
  const userB = uniqueUser();

  const contextA = await browser.newContext();
  const pageA = await contextA.newPage();
  await registerUser(pageA, userA);
  await addExpense(pageA, {
    amount: '15.00',
    categoryName: 'Food',
    date: dayInMonth(currentMonth(), 4),
    note: 'user A only'
  });
  await expect(pageA.getByTestId('kpi-total')).toHaveText('$15.00');

  const contextB = await browser.newContext();
  const pageB = await contextB.newPage();
  await registerUser(pageB, userB);
  await pageB.goto('/');

  await expect(pageB.getByTestId('kpi-total')).toHaveText('$0.00');
  await expect(pageB.getByTestId('recent-item')).toHaveCount(0);
  await expect(pageB.getByText('No recent transactions')).toBeVisible();

  await contextA.close();
  await contextB.close();
});

// AC2: queryKeys factory unit tests (REQ-FE-050 subset).
//
// Frozen titles (docs/issues/t16.md inventory): key shapes are stable and
// prefix-nestable so invalidating a resource root hits every member key.

import { describe, expect, it } from 'vitest';
import { queryKeys } from './query_keys';

const isPrefixOf = (prefix: readonly unknown[], key: readonly unknown[]): boolean =>
  prefix.every((value, index) => key[index] === value);

describe('queryKeys factory', () => {
  it('categories.all is the stable two-element prefix', () => {
    const key = queryKeys.categories.all;
    expect(key).toEqual(['categories', 'list']);
    expect(key.length).toBe(2);
    // Stable across calls (same tuple contents, no per-call randomness).
    expect(queryKeys.categories.all).toEqual(key);
  });

  it('expenses.list embeds the normalized params object under the expenses prefix', () => {
    const key = queryKeys.expenses.list({ page: 2, year_month: '2026-02' });
    expect(key[0]).toBe('expenses');
    expect(key[1]).toBe('list');
    // Params are normalized: fixed key order, undefined dropped.
    expect(key[2]).toEqual({ year_month: '2026-02', page: 2 });
    // Undefined-valued params do not fork the key.
    expect(queryKeys.expenses.list({ page: 2, year_month: undefined })[2]).toEqual(
      queryKeys.expenses.list({ page: 2 })[2]
    );
    expect(queryKeys.expenses.list()[2]).toEqual({});
  });

  it('expenses.detail nests the id under the expenses prefix family', () => {
    const key = queryKeys.expenses.detail('exp-1');
    expect(key).toEqual(['expenses', 'detail', 'exp-1']);
    expect(isPrefixOf(['expenses'], key)).toBe(true);
  });

  it('budgets.byMonth nests the year month under the budgets prefix', () => {
    const key = queryKeys.budgets.byMonth('2026-02');
    expect(key).toEqual(['budgets', 'month', '2026-02']);
    expect(isPrefixOf(['budgets'], key)).toBe(true);
  });

  it('all list and detail keys stay prefix-nestable under their resource root', () => {
    const roots = [
      { root: queryKeys.expenses.root, members: [queryKeys.expenses.list({ page: 1 }), queryKeys.expenses.detail('x')] },
      { root: queryKeys.budgets.root, members: [queryKeys.budgets.byMonth('2026-02')] }
    ];
    for (const { root, members } of roots) {
      for (const member of members) {
        expect(isPrefixOf(root, member)).toBe(true);
      }
    }
    // The categories root prefix likewise prefixes its only member key.
    expect(isPrefixOf(['categories'], queryKeys.categories.all)).toBe(true);
    // Cross-family isolation: invalidating one root never matches another.
    expect(isPrefixOf(['expenses'], queryKeys.budgets.byMonth('2026-02'))).toBe(false);
    expect(isPrefixOf(['budgets'], queryKeys.expenses.detail('x'))).toBe(false);
    expect(isPrefixOf(['categories'], queryKeys.expenses.list({ page: 1 }))).toBe(false);
  });
});

// t20 AC3: the dashboard key family (REQ-FE-050). Two NEW nodes appended;
// the five merged titles above stay byte-identical and are re-run by ac3 as
// the regression proof.

describe('dashboard query keys (ac3)', () => {
  it('the six dashboard keys nest under the single dashboard root prefix', () => {
    const members = [
      queryKeys.dashboard.summary('2026-02'),
      queryKeys.dashboard.byCategory('2026-02'),
      queryKeys.dashboard.trend(),
      queryKeys.dashboard.cumulative('2026-02'),
      queryKeys.dashboard.heatmap(),
      queryKeys.dashboard.recent()
    ];
    // ONE root shared by all six members (the merged invalidation target).
    expect(queryKeys.dashboard.root).toEqual(['dashboard']);
    for (const member of members) {
      expect(isPrefixOf(queryKeys.dashboard.root, member)).toBe(true);
    }
    // The month-driven members nest the driving YYYY-MM (Q2); the
    // `by-category` member key is the literal string, not byCategory.
    expect(queryKeys.dashboard.summary('2026-02')).toEqual([
      'dashboard',
      'summary',
      '2026-02'
    ]);
    expect(queryKeys.dashboard.byCategory('2026-02')).toEqual([
      'dashboard',
      'by-category',
      '2026-02'
    ]);
    expect(queryKeys.dashboard.cumulative('2026-02')).toEqual([
      'dashboard',
      'cumulative',
      '2026-02'
    ]);
    // Six distinct members: no two month-driven keys collide, and no
    // dashboard key leaks into another resource's family.
    expect(new Set(members.map((member) => JSON.stringify(member))).size).toBe(6);
    expect(isPrefixOf(['dashboard'], queryKeys.budgets.byMonth('2026-02'))).toBe(false);
    expect(isPrefixOf(['budgets'], queryKeys.dashboard.summary('2026-02'))).toBe(false);
  });

  it('invalidating the dashboard root prefix-matches every dashboard member key', () => {
    // The merged hooks invalidate exactly this one-line root; prefix
    // matching is what makes that single call cover all six endpoints.
    const root = ['dashboard'];
    const members = [
      queryKeys.dashboard.summary('2026-01'),
      queryKeys.dashboard.summary('2026-02'),
      queryKeys.dashboard.byCategory('2026-02'),
      queryKeys.dashboard.trend(),
      queryKeys.dashboard.cumulative('2026-02'),
      queryKeys.dashboard.heatmap(),
      queryKeys.dashboard.recent()
    ];
    for (const member of members) {
      expect(isPrefixOf(root, member)).toBe(true);
    }
    // Different months of the SAME member both stay under the root, and a
    // sibling resource's key is never matched by the dashboard root.
    expect(isPrefixOf(root, queryKeys.dashboard.summary('2099-12'))).toBe(true);
    expect(isPrefixOf(root, queryKeys.expenses.detail('x'))).toBe(false);
    expect(isPrefixOf(root, queryKeys.categories.all)).toBe(false);
  });
});

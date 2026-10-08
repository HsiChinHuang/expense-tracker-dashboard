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

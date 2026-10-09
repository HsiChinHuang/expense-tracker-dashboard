// queryKeys factory (REQ-FE-050 subset, t16).
//
// One factory object per resource with prefix-nestable families:
//   ["categories"]                      <- categories.all
//   ["expenses"] -> ["expenses","list",norm] / ["expenses","detail",id]
//   ["budgets"]  -> ["budgets","month",ym]
// Invalidating a family root (e.g. ["expenses"]) therefore invalidates
// every member key, which is exactly how the REQ-FE-051 mutation hooks
// refetch mounted observers. The dashboard family arrived in phase_4
// (t16 AC2 / t20 AC3):
//   ["dashboard"] -> summary|by-category|cumulative nested by YYYY-MM,
//                    trend|heatmap|recent under the same root.

import type { ExpenseListParams } from './expenses';

/** Fixed key order so equivalent params serialize to one stable key. */
const PARAM_ORDER = ['year_month', 'category_id', 'page', 'page_size'] as const;

/**
 * Normalize list params for a stable query key: keys are emitted in a
 * fixed order and `undefined` values are dropped, so `{page: 2}` and
 * `{page: 2, year_month: undefined}` map to the same key object.
 */
export const normalizeListParams = (
  params?: ExpenseListParams
): Record<string, string | number> => {
  const normalized: Record<string, string | number> = {};
  if (params) {
    for (const key of PARAM_ORDER) {
      const value = params[key];
      if (value !== undefined) {
        normalized[key] = value;
      }
    }
  }
  return normalized;
};

/** Stable query-key factory shared by hooks and invalidation calls. */
export const queryKeys = {
  categories: {
    /** Stable two-element prefix for the category list. */
    all: ['categories', 'list'] as const
  },
  expenses: {
    /** Family root shared by every expense key. */
    root: ['expenses'] as const,
    /** Params-carrying list key (normalized, nested under the root). */
    list: (params?: ExpenseListParams) =>
      ['expenses', 'list', normalizeListParams(params)] as const,
    /** Single-expense key nested under the same root. */
    detail: (id: string) => ['expenses', 'detail', id] as const
  },
  budgets: {
    /** Family root shared by every budget key. */
    root: ['budgets'] as const,
    /** One month's key nested under the budgets root. */
    byMonth: (yearMonth: string) => ['budgets', 'month', yearMonth] as const
  },
  dashboard: {
    /** Family root: invalidating it hits all six dashboard members. */
    root: ['dashboard'] as const,
    /** Month-driven summary key (REQ-FE-051 invalidation reaches it). */
    summary: (yearMonth: string) => ['dashboard', 'summary', yearMonth] as const,
    /** Category breakdown; the `by-category` key string is pinned (Q1). */
    byCategory: (yearMonth: string) => ['dashboard', 'by-category', yearMonth] as const,
    /** Trend key (param-driven; Builder choice under the root, Q2). */
    trend: () => ['dashboard', 'trend'] as const,
    /** Month-driven cumulative key. */
    cumulative: (yearMonth: string) => ['dashboard', 'cumulative', yearMonth] as const,
    /** Heatmap key (param-driven). */
    heatmap: () => ['dashboard', 'heatmap'] as const,
    /** Recent-items key (param-driven). */
    recent: () => ['dashboard', 'recent'] as const
  }
};

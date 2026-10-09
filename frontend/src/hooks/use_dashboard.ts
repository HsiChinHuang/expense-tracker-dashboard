/* eslint-disable react-hooks/rules-of-hooks -- the project coding standard
pins snake_case hook names (use_dashboard); eslint-plugin-react-hooks only
recognizes usePascalCase, so the recognition false-positive is scoped off
here while the Rules of Hooks are still followed by construction. */
// Dashboard data hooks (REQ-FE-051 observability, REQ-ARCH-032, t20).
//
// Six parallel read hooks (REQ-ARCH-032), each keyed through
// queryKeys.dashboard so the ALREADY-MERGED expense/budget mutation
// invalidations (`invalidateQueries({queryKey: ["dashboard"]})` in
// use_expenses.ts / use_budget.ts) reach them — this issue makes that
// invalidation OBSERVABLE (REQ-FE-051). The month-driven hooks (summary,
// by-category, cumulative) read the month from MonthContext via useMonth,
// so a month change re-keys them and refetches the new year_month;
// trend/heatmap/recent are param-driven and month-independent.
// Category mutations invalidate ["categories"] only, so they never touch
// these keys (the merged negative control).

import { useQuery } from '@tanstack/react-query';
import {
  getByCategory,
  getCumulative,
  getHeatmap,
  getRecent,
  getSummary,
  getTrend
} from '../api/dashboard';
import { queryKeys } from '../api/query_keys';
import { useMonth } from '../context/month_context';

/** Summary for the context month, keyed under ["dashboard","summary",ym]. */
export const use_summary = () => {
  const { yearMonth } = useMonth();
  return useQuery({
    queryKey: queryKeys.dashboard.summary(yearMonth),
    queryFn: () => getSummary(yearMonth)
  });
};

/** Category breakdown for the context month (five frozen row keys). */
export const use_by_category = () => {
  const { yearMonth } = useMonth();
  return useQuery({
    queryKey: queryKeys.dashboard.byCategory(yearMonth),
    queryFn: () => getByCategory(yearMonth)
  });
};

/** Rolling trend (month-independent; key is Builder choice under the root). */
export const use_trend = (months?: number) =>
  useQuery({
    queryKey: queryKeys.dashboard.trend(),
    queryFn: () => getTrend(months)
  });

/** Daily cumulative curve for the context month. */
export const use_cumulative = () => {
  const { yearMonth } = useMonth();
  return useQuery({
    queryKey: queryKeys.dashboard.cumulative(yearMonth),
    queryFn: () => getCumulative(yearMonth)
  });
};

/** Heatmap grid (month-independent). */
export const use_heatmap = (weeks?: number) =>
  useQuery({
    queryKey: queryKeys.dashboard.heatmap(),
    queryFn: () => getHeatmap(weeks)
  });

/** Recent expenses in the merged ten-key shape (month-independent). */
export const use_recent = (limit?: number) =>
  useQuery({
    queryKey: queryKeys.dashboard.recent(),
    queryFn: () => getRecent(limit)
  });

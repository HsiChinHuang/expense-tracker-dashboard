// Typed dashboard API module (REQ-ARCH-032 frontend half, t19 contract mirror).
//
// One function per merged /api/v1/dashboard/* endpoint, 1:1, through the
// shared `api` instance (REQ-ARCH-070) — this module imports `./client` and
// NEVER axios directly. Money fields stay the frozen 2-decimal STRINGS the
// merged t19 service returns and `percentage` is a JSON NUMBER or null
// (`round(total / budget * 100, 1) if budget > 0 else None`); this module
// performs NO numeric coercion anywhere (REQ-PROD-023 / REQ-SEC-050).
//
// Pages, components and context import NEITHER this module NOR axios: the
// six hooks in `hooks/use_dashboard.ts` are the only consumers (t20 ac2).

import { api } from './client';
import type { Expense } from './expenses';

/** GET /summary — the seven frozen keys (service lines 213-220). */
export interface DashboardSummary {
  /** `YYYY-MM` query echo. */
  year_month: string;
  /** Month total, 2-decimal string. */
  total: string;
  /** Month budget, 2-decimal string ("0.00" when absent). */
  budget_amount: string;
  /** budget_amount - total, 2-decimal string (may be negative). */
  remaining: string;
  /** Percent of budget spent — a JSON number, or null when no budget. */
  percentage: number | null;
  is_over_budget: boolean;
  category_count: number;
}

/** One by-category row — the frozen five keys. */
export interface DashboardCategoryRow {
  category_id: string;
  category_name: string;
  /** Category color, null when the row carries none. */
  color: string | null;
  /** Row amount, 2-decimal string. */
  amount: string;
  /** Share of the month total, a JSON number. */
  percentage: number;
}

/** GET /by-category — the frozen three keys. */
export interface DashboardByCategory {
  year_month: string;
  total: string;
  categories: DashboardCategoryRow[];
}

/** One trend bucket — EXACTLY two keys (no label key, merged truth). */
export interface DashboardTrendMonth {
  year_month: string;
  total: string;
}

/** GET /trend — the single-key wrapper. */
export interface DashboardTrend {
  months: DashboardTrendMonth[];
}

/** One cumulative day row — the frozen three keys. */
export interface DashboardCumulativeDay {
  /** Calendar date, `YYYY-MM-DD`. */
  date: string;
  /** That day's spend, 2-decimal string. */
  daily: string;
  /** Running total through that day, 2-decimal string. */
  cumulative: string;
}

/** GET /cumulative — the frozen three keys. */
export interface DashboardCumulative {
  year_month: string;
  budget: string;
  days: DashboardCumulativeDay[];
}

/** One heatmap week: Monday week_start plus exactly seven days. */
export interface DashboardHeatmapWeek {
  week_start: string;
  days: Array<{ date: string; amount: string }>;
}

/** GET /heatmap — the frozen two keys. */
export interface DashboardHeatmap {
  /** Largest daily amount in the window, 2-decimal string. */
  max_amount: string;
  weeks: DashboardHeatmapWeek[];
}

/** GET /recent — items reuse the merged ten-key expense shape. */
export interface DashboardRecent {
  items: Expense[];
}

/** Month summary for one `YYYY-MM`. */
export const getSummary = async (yearMonth: string): Promise<DashboardSummary> => {
  const response = await api.get<DashboardSummary>('/api/v1/dashboard/summary', {
    params: { year_month: yearMonth }
  });
  return response.data;
};

/** Category breakdown for one `YYYY-MM`. */
export const getByCategory = async (yearMonth: string): Promise<DashboardByCategory> => {
  const response = await api.get<DashboardByCategory>('/api/v1/dashboard/by-category', {
    params: { year_month: yearMonth }
  });
  return response.data;
};

/** Rolling `months`-bucket trend (merged default 6, bounded 1..24). */
export const getTrend = async (months?: number): Promise<DashboardTrend> => {
  const response = await api.get<DashboardTrend>('/api/v1/dashboard/trend', {
    params: { months }
  });
  return response.data;
};

/** Daily cumulative curve for one `YYYY-MM`. */
export const getCumulative = async (yearMonth: string): Promise<DashboardCumulative> => {
  const response = await api.get<DashboardCumulative>('/api/v1/dashboard/cumulative', {
    params: { year_month: yearMonth }
  });
  return response.data;
};

/** GitHub-style `weeks`-week grid (merged default 12, bounded 1..52). */
export const getHeatmap = async (weeks?: number): Promise<DashboardHeatmap> => {
  const response = await api.get<DashboardHeatmap>('/api/v1/dashboard/heatmap', {
    params: { weeks }
  });
  return response.data;
};

/** Newest expenses (merged default 10, bounded 1..50) in the ten-key shape. */
export const getRecent = async (limit?: number): Promise<DashboardRecent> => {
  const response = await api.get<DashboardRecent>('/api/v1/dashboard/recent', {
    params: { limit }
  });
  return response.data;
};

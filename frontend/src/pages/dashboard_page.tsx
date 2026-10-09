// DashboardPage — the dashboard integration surface (REQ-FE-062, REQ-FE-074,
// REQ-FE-100, REQ-ARCH-032, REQ-FE-015; t22).
//
// This is the ONLY new module that calls the six t20 hooks (Q1): the page
// mounts all six on render (six parallel requests, REQ-ARCH-032) and feeds
// each presentational child its own slice — CategoryPieChart from
// by-category, MonthlyTrendChart from trend, CumulativeLineChart from
// cumulative (the reference budget from the summary), WeeklyHeatmap from
// heatmap, BudgetProgress from summary, and the recent list from recent.
// The month lives in MonthContext (REQ-FE-032): the MonthPicker in the
// header steps it and every month-driven hook re-keys together, so a switch
// (even a rapid one) settles on the latest selection.
//
// Money renders VERBATIM from the API strings (REQ-PROD-023): amounts are
// backtick '$'-prefix concatenations, never re-formatted. A null percentage
// is BudgetProgress's "No budget set" affordance (REQ-PROD-033). Loading
// renders animate-pulse skeleton blocks inside role="status" regions per
// section (REQ-FE-100); a failed query renders the t20 ErrorState whose
// Retry refetches that query (REQ-FE-102). The user menu is the simplest
// accessible affordance (Q8): username + a plain Log out on the merged
// AuthContext.logout.

import { useEffect, type ReactNode } from 'react';
import {
  use_by_category,
  use_cumulative,
  use_heatmap,
  use_recent,
  use_summary,
  use_trend
} from '../hooks/use_dashboard';
import { useAuth } from '../context/auth_context';
import { CategoryPieChart } from '../components/charts/category_pie_chart';
import { MonthlyTrendChart } from '../components/charts/monthly_trend_chart';
import { CumulativeLineChart } from '../components/charts/cumulative_line_chart';
import { WeeklyHeatmap } from '../components/charts/weekly_heatmap';
import { BudgetProgress } from '../components/common/budget_progress';
import { MonthPicker } from '../components/common/month_picker';
import { EmptyState } from '../components/ui/empty_state';
import { ErrorState } from '../components/ui/error_state';

/** Skeleton block: animate-pulse placeholders inside a status region. */
const SkeletonBlock = ({ label }: { label: string }): JSX.Element => (
  <div role="status" aria-label={label} className="space-y-2">
    <div className="animate-pulse h-4 w-1/2 rounded bg-slate-200" />
    <div className="animate-pulse h-24 rounded bg-slate-200" />
  </div>
);

/** One labelled dashboard panel wrapping a section's own query state. */
const Panel = ({
  title,
  children
}: {
  title: string;
  children: ReactNode;
}): JSX.Element => (
  <section className="rounded-lg bg-white p-4 shadow">
    <h2 className="mb-2 text-sm font-semibold text-slate-700">{title}</h2>
    {children}
  </section>
);

export const DashboardPage = (): JSX.Element => {
  const { user, logout } = useAuth();
  const summary = use_summary();
  const byCategory = use_by_category();
  const trend = use_trend();
  const cumulative = use_cumulative();
  const heatmap = use_heatmap();
  const recent = use_recent();

  useEffect(() => {
    document.title = 'Dashboard';
  }, []);

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span aria-hidden="true" className="text-2xl" data-testid="dashboard-logo">
            ●
          </span>
          <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
          <MonthPicker />
        </div>
        <div className="flex items-center gap-2" data-testid="user-menu">
          <span className="text-sm text-slate-600">{user?.username ?? 'Account'}</span>
          <button
            type="button"
            onClick={logout}
            className="rounded border border-slate-300 px-2 py-1 text-sm text-slate-700"
          >
            Log out
          </button>
        </div>
      </header>

      <Panel title="Overview">
        {summary.isPending ? (
          <SkeletonBlock label="Loading summary" />
        ) : summary.isError ? (
          <ErrorState
            message="Could not load the dashboard summary"
            onRetry={() => {
              void summary.refetch();
            }}
          />
        ) : summary.data === undefined ? null : (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded border border-slate-200 p-3">
              <p className="text-sm text-slate-500">Total spent</p>
              <p className="text-xl font-semibold" data-testid="kpi-total">
                {`$${summary.data.total}`}
              </p>
            </div>
            <div className="rounded border border-slate-200 p-3">
              <p className="text-sm text-slate-500">Budget</p>
              <p className="text-xl font-semibold" data-testid="kpi-budget">
                {`$${summary.data.budget_amount}`}
              </p>
            </div>
            <div className="rounded border border-slate-200 p-3">
              <p className="text-sm text-slate-500">Remaining</p>
              <p className="text-xl font-semibold" data-testid="kpi-remaining">
                {`$${summary.data.remaining}`}
              </p>
            </div>
            <div className="rounded border border-slate-200 p-3">
              <p className="text-sm text-slate-500">Categories</p>
              <p className="text-xl font-semibold" data-testid="kpi-categories">
                {summary.data.category_count}
              </p>
            </div>
          </div>
        )}
      </Panel>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Spending by category">
          {byCategory.isPending ? (
            <SkeletonBlock label="Loading category breakdown" />
          ) : byCategory.isError ? (
            <ErrorState
              message="Could not load the category breakdown"
              onRetry={() => {
                void byCategory.refetch();
              }}
            />
          ) : byCategory.data === undefined ? null : (
            <CategoryPieChart categories={byCategory.data.categories} />
          )}
        </Panel>

        <Panel title="Monthly trend">
          {trend.isPending ? (
            <SkeletonBlock label="Loading trend" />
          ) : trend.isError ? (
            <ErrorState
              message="Could not load the monthly trend"
              onRetry={() => {
                void trend.refetch();
              }}
            />
          ) : trend.data === undefined ? null : (
            <MonthlyTrendChart months={trend.data.months} />
          )}
        </Panel>

        <Panel title="Cumulative spending">
          {cumulative.isPending ? (
            <SkeletonBlock label="Loading cumulative spending" />
          ) : cumulative.isError ? (
            <ErrorState
              message="Could not load cumulative spending"
              onRetry={() => {
                void cumulative.refetch();
              }}
            />
          ) : cumulative.data === undefined ? null : (
            <CumulativeLineChart
              budget={cumulative.data.budget}
              days={cumulative.data.days}
            />
          )}
        </Panel>

        <Panel title="Daily activity">
          {heatmap.isPending ? (
            <SkeletonBlock label="Loading activity heatmap" />
          ) : heatmap.isError ? (
            <ErrorState
              message="Could not load the activity heatmap"
              onRetry={() => {
                void heatmap.refetch();
              }}
            />
          ) : heatmap.data === undefined ? null : (
            <WeeklyHeatmap max_amount={heatmap.data.max_amount} weeks={heatmap.data.weeks} />
          )}
        </Panel>

        <Panel title="Budget progress">
          {summary.isPending ? (
            <SkeletonBlock label="Loading budget progress" />
          ) : summary.isError ? (
            <ErrorState
              message="Could not load the budget progress"
              onRetry={() => {
                void summary.refetch();
              }}
            />
          ) : summary.data === undefined ? null : (
            <BudgetProgress
              percentage={summary.data.percentage}
              total={summary.data.total}
              budget={summary.data.budget_amount}
              is_over_budget={summary.data.is_over_budget}
            />
          )}
        </Panel>

        <Panel title="Recent transactions">
          {recent.isPending ? (
            <SkeletonBlock label="Loading recent transactions" />
          ) : recent.isError ? (
            <ErrorState
              message="Could not load recent transactions"
              onRetry={() => {
                void recent.refetch();
              }}
            />
          ) : recent.data === undefined ? null : recent.data.items.length === 0 ? (
            <EmptyState title="No recent transactions" />
          ) : (
            <ul className="space-y-2">
              {recent.data.items.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between rounded border border-slate-200 p-2"
                  data-testid="recent-item"
                >
                  <span>{item.category_name}</span>
                  <span className="text-slate-500">{item.date}</span>
                  <span className="font-medium" data-testid="recent-amount">
                    {`$${item.amount}`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>
    </div>
  );
};

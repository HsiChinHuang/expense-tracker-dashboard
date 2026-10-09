// MonthlyTrendChart (REQ-FE-071, REQ-PROD-033, REQ-FE-110; t21 ac3).
//
// PRESENTATIONAL BarChart over the merged t20 trend shape
// `{year_month, total}` — the wire carries NO label key, so the component
// derives its own `MMM YY` label through the SHARED stdlib helper
// `formatMonthLabel` in `utils/chart_data.ts` — pure string math over the
// `YYYY-MM` key, no locale/date-object formatting anywhere (grep-pinned).
//
// Zero-month semantics (Q5): a `0.00` month keeps its axis label and bar
// slot (a zero-height bar); only an ALL-ZERO or empty window is "empty"
// and renders the merged t20 EmptyState with the pinned title.
//
// The responsive wrapper stays banned (no ResizeObserver in this jsdom):
// explicit width/height only.

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts';
import { EmptyState } from '../ui/empty_state';
import { formatMonthLabel, formatUsdTick, toNumber } from '../../utils/chart_data';

/** One trend bucket — mirrors the merged t20 wire shape (no label key). */
export interface TrendMonth {
  year_month: string;
  /** Month total, 2-decimal money string. */
  total: string;
}

interface MonthlyTrendChartProps {
  months: TrendMonth[];
}

interface TrendBar {
  /** `MMM YY` axis label from the shared stdlib helper. */
  label: string;
  /** Bar geometry value via the audited helper bridge. */
  value: number;
  /** Money string for the tooltip — VERBATIM API value. */
  total: string;
}

const TREND_WINDOW = 6;

/** REQ-FE-071 pinned bar color (Chapter8 §8.11.2). */
const TREND_BAR_BLUE = '#3B82F6';

export const MonthlyTrendChart = ({ months }: MonthlyTrendChartProps): JSX.Element => {
  const window = months.slice(0, TREND_WINDOW);
  const allZero = window.every((month) => toNumber(month.total) === 0);
  if (window.length === 0 || allZero) {
    return <EmptyState title="No data for this period" />;
  }
  const bars: TrendBar[] = window.map((month) => ({
    label: formatMonthLabel(month.year_month),
    value: toNumber(month.total),
    total: month.total
  }));
  return (
    <div
      role="img"
      aria-label="Monthly spending trend bar chart"
      data-testid="monthly-trend-chart"
    >
      <BarChart data={bars} width={560} height={320}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" />
        <YAxis tickFormatter={formatUsdTick} />
        <Bar
          dataKey="value"
          fill={TREND_BAR_BLUE}
          name="Month total"
          isAnimationActive={false}
        />
      </BarChart>
    </div>
  );
};

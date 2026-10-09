// CumulativeLineChart (REQ-FE-072, REQ-PROD-014, REQ-FE-110; t21 ac4).
//
// PRESENTATIONAL LineChart over the merged t20 cumulative shape
// `{year_month, budget, days:[{date, daily, cumulative}]}`. The curve is
// the pinned blue while cumulative never EXCEEDS the budget and turns the
// pinned red the moment any point is strictly over it — the boundary is
// `>`, not `>=`, so exactly-at-budget stays blue. The budget itself is a
// dashed grey ReferenceLine. All comparisons run through the audited
// cents-exact helpers; this component never coerces money itself.
//
// Empty `days` -> the merged t20 EmptyState with the pinned title.
// The responsive wrapper stays banned: explicit width/height only.

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  XAxis,
  YAxis
} from 'recharts';
import { EmptyState } from '../ui/empty_state';
import { exceeds, formatUsdTick, toNumber } from '../../utils/chart_data';

/** One cumulative day row — mirrors the merged t20 wire shape. */
export interface CumulativeDay {
  /** Calendar date, `YYYY-MM-DD`. */
  date: string;
  /** That day's spend, 2-decimal money string. */
  daily: string;
  /** Running total through that day, 2-decimal money string. */
  cumulative: string;
}

interface CumulativeLineChartProps {
  /** Month budget, 2-decimal money string. */
  budget: string;
  days: CumulativeDay[];
}

/** Chapter8 §8.11.2 frozen strokes: under-budget blue, over-budget red,
 *  budget reference line dashed grey. */
const LINE_BLUE = '#3B82F6';
const LINE_RED = '#EF4444';
const BUDGET_GREY = '#9CA3AF';

interface CumulativePoint {
  /** Day-of-month tick label from the date string (stdlib slice math). */
  day: string;
  /** Line geometry value via the audited helper bridge. */
  value: number;
}

export const CumulativeLineChart = ({
  budget,
  days
}: CumulativeLineChartProps): JSX.Element => {
  if (days.length === 0) {
    return <EmptyState title="No spending this month" />;
  }
  const overBudget = days.some((day) => exceeds(day.cumulative, budget));
  const points: CumulativePoint[] = days.map((day) => ({
    day: day.date.slice(8),
    value: toNumber(day.cumulative)
  }));
  return (
    <div
      role="img"
      aria-label="Cumulative spending line chart"
      data-testid="cumulative-line-chart"
    >
      <LineChart data={points} width={560} height={320}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis tickFormatter={formatUsdTick} />
        <Line
          dataKey="value"
          name="Cumulative"
          stroke={overBudget ? LINE_RED : LINE_BLUE}
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
        <ReferenceLine
          y={toNumber(budget)}
          stroke={BUDGET_GREY}
          strokeDasharray="6 4"
          ifOverflow="extendDomain"
        />
      </LineChart>
    </div>
  );
};

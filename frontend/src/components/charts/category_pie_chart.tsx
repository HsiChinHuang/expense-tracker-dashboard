// CategoryPieChart (REQ-FE-070, REQ-PROD-033, REQ-FE-110; t21 ac2).
//
// PRESENTATIONAL: data arrives via plain props (the merged t20 wire shape
// `{category_id, category_name, color, amount, percentage}`); this module
// performs NO data fetching and imports NO hook or api client (t22 wires
// it to the dashboard category hook). Empty list -> the merged t20
// EmptyState with the pinned title.
//
// Top-6 + Other (REQ-PROD-033): more than six rows render as the six
// largest API slices plus one synthetic `Other` slice whose amount is the
// DECIMAL-SAFE sum of the merged tail (via the audited cents helper — the
// component itself never coerces money). Slice geometry needs numbers, so
// the dataKey reads the API `percentage` (Q4): the DOM never sees a
// recomputed money value, amounts render VERBATIM from the API string.
//
// The responsive wrapper stays banned (ResizeObserver is undefined in
// this jsdom), so the chart carries explicit width/height.

import { Cell, Legend, Pie, PieChart, Tooltip } from 'recharts';
import { EmptyState } from '../ui/empty_state';
import { sumAmounts, sumPercentages } from '../../utils/chart_data';

/** One by-category row — mirrors the merged t20 wire shape. */
export interface CategoryPieRow {
  category_id: string;
  category_name: string;
  /** Category color from the API; rendered VERBATIM as the slice fill. */
  color: string | null;
  /** 2-decimal money string; rendered VERBATIM, never re-formatted. */
  amount: string;
  /** Share of the month total — the numeric dataKey for slice geometry. */
  percentage: number;
}

interface CategoryPieChartProps {
  categories: CategoryPieRow[];
}

interface PieSlice {
  key: string;
  name: string;
  /** Money string for the tooltip — VERBATIM API value or cents-exact sum. */
  amount: string;
  /** Numeric dataKey (API percentage, or the decimal-safe Other sum). */
  value: number;
  /** Percentage as display text (pre-formatted, no component coercion). */
  percentageText: string;
  fill: string;
}

const FALLBACK_SLICE_COLOR = '#94A3B8';
const OTHER_LABEL = 'Other';

/** Custom tooltip: name + `$`-prefixed amount + percentage, DOM-visible. */
const CategoryTooltip = ({
  active,
  payload
}: {
  active?: boolean;
  payload?: Array<{ payload?: PieSlice }>;
}): JSX.Element | null => {
  const slice = payload?.[0]?.payload;
  if (!active || slice === undefined) {
    return null;
  }
  return (
    <div>
      <span>{slice.name}</span>
      <span>{`$${slice.amount}`}</span>
      <span>{slice.percentageText}</span>
    </div>
  );
};

/** Merge the tail beyond the top six into one decimal-safe `Other` slice. */
const toSlices = (categories: CategoryPieRow[]): PieSlice[] => {
  const head = categories.slice(0, 6).map((row) => ({
    key: row.category_id,
    name: row.category_name,
    amount: row.amount,
    value: row.percentage,
    percentageText: `${row.percentage}%`,
    fill: row.color ?? FALLBACK_SLICE_COLOR
  }));
  const tail = categories.slice(6);
  if (tail.length === 0) {
    return head;
  }
  return [
    ...head,
    {
      key: 'other',
      name: OTHER_LABEL,
      amount: sumAmounts(tail.map((row) => row.amount)),
      value: sumPercentages(tail.map((row) => row.percentage)),
      percentageText: `${sumPercentages(tail.map((row) => row.percentage))}%`,
      fill: FALLBACK_SLICE_COLOR
    }
  ];
};

export const CategoryPieChart = ({ categories }: CategoryPieChartProps): JSX.Element => {
  if (categories.length === 0) {
    return <EmptyState title="No expenses this month" />;
  }
  const slices = toSlices(categories);
  return (
    <div
      role="img"
      aria-label="Spending by category pie chart"
      data-testid="category-pie-chart"
    >
      <PieChart width={420} height={320}>
        <Pie
          data={slices}
          dataKey="value"
          nameKey="name"
          outerRadius={110}
          isAnimationActive={false}
        >
          {slices.map((slice) => (
            <Cell key={slice.key} fill={slice.fill} />
          ))}
        </Pie>
        <Tooltip content={<CategoryTooltip />} />
        <Legend />
      </PieChart>
    </div>
  );
};

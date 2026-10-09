// WeeklyHeatmap (REQ-FE-073; t21 ac5).
//
// DELIBERATELY a CUSTOM div grid — per the requirement this surface is NOT
// one of the charting-library charts (the library name may not even appear
// in this file). It exposes role="grid" with role="gridcell" day cells;
// every day of the window renders a cell, missing days included, in the
// zero color. Cell shades escalate against the window maximum through the
// pinned ramp via the audited helper (exact cross-multiplied cents — no
// float division, no divide-by-zero when the maximum is "0.00").
//
// Each cell exposes `<date> $<amount>` to assistive technology via
// aria-label (Q7). Empty window -> the merged t20 EmptyState with the
// pinned title instead of a grid. PRESENTATIONAL: plain data props only.

import { EmptyState } from '../ui/empty_state';
import { ratioAtLeast, toNumber } from '../../utils/chart_data';

/** One heatmap week — mirrors the merged t20 wire shape. */
export interface HeatmapWeek {
  week_start: string;
  days: Array<{ date: string; amount: string }>;
}

interface WeeklyHeatmapProps {
  /** Largest daily amount in the window, 2-decimal money string. */
  max_amount: string;
  weeks: HeatmapWeek[];
}

/** Five-way scale: zero color #F3F4F6, then the four pinned shades. */
const HEAT_SCALE = ['#F3F4F6', '#DBEAFE', '#93C5FD', '#3B82F6', '#1E40AF'] as const;

const cellColor = (amount: string, maximum: string): string => {
  if (toNumber(maximum) <= 0 || toNumber(amount) <= 0) {
    return HEAT_SCALE[0] ?? '#F3F4F6';
  }
  if (ratioAtLeast(amount, 1, 1, maximum)) {
    return HEAT_SCALE[4] ?? '#1E40AF';
  }
  if (ratioAtLeast(amount, 3, 4, maximum)) {
    return HEAT_SCALE[3] ?? '#3B82F6';
  }
  if (ratioAtLeast(amount, 1, 2, maximum)) {
    return HEAT_SCALE[2] ?? '#93C5FD';
  }
  if (ratioAtLeast(amount, 1, 100, maximum)) {
    return HEAT_SCALE[1] ?? '#DBEAFE';
  }
  return HEAT_SCALE[0] ?? '#F3F4F6';
};

export const WeeklyHeatmap = ({ max_amount, weeks }: WeeklyHeatmapProps): JSX.Element => {
  if (weeks.length === 0) {
    return <EmptyState title="No activity in this window" />;
  }
  return (
    <div
      role="grid"
      aria-label="Weekly spending heatmap grid"
      data-testid="weekly-heatmap"
    >
      {weeks.map((week) => (
        <div role="row" key={week.week_start} data-testid="heatmap-week">
          {week.days.map((day) => (
            <div
              role="gridcell"
              key={day.date}
              aria-label={`${day.date} $${day.amount}`}
              title={`${day.date} $${day.amount}`}
              style={{ backgroundColor: cellColor(day.amount, max_amount) }}
            />
          ))}
        </div>
      ))}
    </div>
  );
};

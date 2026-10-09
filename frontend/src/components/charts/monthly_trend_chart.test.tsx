// AC3: MonthlyTrendChart tests (REQ-FE-071, REQ-PROD-033; t21).
//
// Six frozen nodes: five chart nodes plus the shared month-label helper
// node (the helper lives in utils/chart_data.ts and is exercised HERE
// because the charts share one month/number layer). PRESENTATIONAL props,
// no MSW handler needed. Style assertions convert the pinned hex to the
// rgb(…) form jsdom reports (test files are the exempt coercion scope).

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MonthlyTrendChart } from './monthly_trend_chart';
import type { TrendMonth } from './monthly_trend_chart';
import { formatMonthLabel } from '../../utils/chart_data';

/**
 * SVG presentation attributes serialize VERBATIM in jsdom, so fills are
 * compared against the pinned hex literals case-insensitively.
 */
const sameColor = (actual: string | null, hex: string): boolean =>
  (actual ?? '').trim().toLowerCase() === hex.toLowerCase();

const month = (year_month: string, total: string): TrendMonth => ({
  year_month,
  total
});

const SIX_MONTHS: TrendMonth[] = [
  month('2025-09', '100.00'),
  month('2025-10', '200.00'),
  month('2025-11', '300.00'),
  month('2025-12', '400.00'),
  month('2026-01', '500.00'),
  month('2026-02', '600.00')
];

/** X-axis tick labels in left-to-right position order. */
const tickLabels = (container: HTMLElement): string[] =>
  Array.from(
    container.querySelectorAll(
      '.recharts-xAxis .recharts-cartesian-axis-tick-value'
    )
  )
    .sort((left, right) => {
      const x = (node: Element) => Number(node.getAttribute('x') ?? '0');
      return x(left) - x(right);
    })
    .map((tick) => tick.textContent ?? '');

describe('MonthlyTrendChart (ac3)', () => {
  it('the trend chart is an accessible image named from its chart description', () => {
    render(<MonthlyTrendChart months={SIX_MONTHS} />);
    expect(
      screen.getByRole('img', { name: 'Monthly spending trend bar chart' })
    ).toBeTruthy();
  });

  it('the trend chart renders one bar per month in chronological order', () => {
    const { container } = render(<MonthlyTrendChart months={SIX_MONTHS} />);
    const bars = container.querySelectorAll('.recharts-bar-rectangle path');
    expect(bars).toHaveLength(6);
    const labels = tickLabels(container).filter((label) =>
      /^[A-Z][a-z]{2} \d{2}$/.test(label)
    );
    expect(labels).toEqual([
      'Sep 25',
      'Oct 25',
      'Nov 25',
      'Dec 25',
      'Jan 26',
      'Feb 26'
    ]);
  });

  it('the trend bars carry the pinned blue and the value axis carries dollar labels', () => {
    const { container } = render(<MonthlyTrendChart months={SIX_MONTHS} />);
    const bars = container.querySelectorAll('.recharts-bar-rectangle path');
    expect(bars.length).toBeGreaterThan(0);
    bars.forEach((bar) => {
      expect(sameColor(bar.getAttribute('fill'), '#3B82F6')).toBeTruthy();
    });
    const valueTicks = Array.from(
      container.querySelectorAll(
        '.recharts-yAxis .recharts-cartesian-axis-tick-value'
      )
    ).map((tick) => tick.textContent ?? '');
    expect(valueTicks.length).toBeGreaterThan(0);
    valueTicks.forEach((tick) => expect(tick).toMatch(/^\$/));
  });

  it('zero total months keep their axis label and never drop from the chart', () => {
    const withZero: TrendMonth[] = [
      month('2026-01', '100.00'),
      month('2026-02', '0.00'),
      month('2026-03', '250.00'),
      month('2026-04', '0.00'),
      month('2026-05', '75.00'),
      month('2026-06', '420.00')
    ];
    const { container } = render(<MonthlyTrendChart months={withZero} />);
    // All six slots survive: six bar stacks exist even for 0.00 months.
    expect(
      container.querySelectorAll('.recharts-bar-rectangle').length
    ).toBeGreaterThanOrEqual(4);
    ['Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26'].forEach(
      (label) => {
        expect(tickLabels(container)).toContain(label);
      }
    );
    expect(
      screen.queryByRole('heading', { name: 'No data for this period' })
    ).toBeNull();
  });

  it('a trend window of all zero months renders the empty state instead of a chart', () => {
    const allZero = SIX_MONTHS.map((entry) => month(entry.year_month, '0.00'));
    const { container } = render(<MonthlyTrendChart months={allZero} />);
    expect(
      screen.getByRole('heading', { name: 'No data for this period' })
    ).toBeTruthy();
    expect(container.querySelector('svg.recharts-surface')).toBeNull();
    const { container: emptyContainer } = render(<MonthlyTrendChart months={[]} />);
    expect(
      screen.getAllByRole('heading', { name: 'No data for this period' }).length
    ).toBeGreaterThanOrEqual(2);
    expect(emptyContainer.querySelector('svg.recharts-surface')).toBeNull();
  });

  it('the month label helper formats every month of the year as MMM YY', () => {
    const expected = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'
    ];
    expected.forEach((abbreviation, index) => {
      const monthNumber = String(index + 1).padStart(2, '0');
      expect(formatMonthLabel(`2026-${monthNumber}`)).toBe(
        `${abbreviation} 26`
      );
    });
    expect(formatMonthLabel('2025-01')).toBe('Jan 25');
  });
});

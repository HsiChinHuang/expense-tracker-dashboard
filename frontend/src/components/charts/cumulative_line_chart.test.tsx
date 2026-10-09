// AC4: CumulativeLineChart tests (REQ-FE-072, REQ-PROD-014; t21).
//
// Five frozen nodes. The sharp edge is the `>` (not `>=`) over-budget
// boundary: exactly-at-budget keeps the pinned blue, one cent over flips
// the curve to the pinned red. Style assertions read the SVG <path>
// stroke; the reference line is asserted dashed-grey via its attributes.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CumulativeLineChart } from './cumulative_line_chart';
import type { CumulativeDay } from './cumulative_line_chart';

/**
 * SVG presentation attributes (stroke/fill) are serialized VERBATIM by
 * jsdom, so assertions compare the pinned hex literals case-insensitively
 * — no hex→rgb coercion needed anywhere in this file.
 */
const sameColor = (actual: string | null, hex: string): boolean =>
  (actual ?? '').trim().toLowerCase() === hex.toLowerCase();

const day = (date: string, daily: string, cumulative: string): CumulativeDay => ({
  date,
  daily,
  cumulative
});

const UNDER_DAYS: CumulativeDay[] = [
  day('2026-02-01', '100.00', '100.00'),
  day('2026-02-02', '150.00', '250.00'),
  day('2026-02-03', '100.00', '350.00')
];

/** Curve <path> elements: the data line carries a stroke, the grid not. */
const curveStrokes = (container: HTMLElement): string[] =>
  Array.from(container.querySelectorAll('.recharts-line-curve')).map((path) =>
    (path.getAttribute('stroke') ?? '').trim()
  );

describe('CumulativeLineChart (ac4)', () => {
  it('the line stays blue when cumulative spending exactly equals the budget', () => {
    const exactDays: CumulativeDay[] = [
      ...UNDER_DAYS,
      day('2026-02-04', '150.00', '500.00') // cumulative == budget exactly
    ];
    const { container } = render(
      <CumulativeLineChart budget="500.00" days={exactDays} />
    );
    const strokes = curveStrokes(container);
    expect(strokes).toHaveLength(1);
    expect(sameColor(strokes[0] ?? null, '#3B82F6')).toBeTruthy();
  });

  it('the line turns red when cumulative spending exceeds the budget', () => {
    const overDays: CumulativeDay[] = [
      ...UNDER_DAYS,
      day('2026-02-04', '0.01', '500.01') // one cent over the budget
    ];
    const { container } = render(
      <CumulativeLineChart budget="500.00" days={overDays} />
    );
    const strokes = curveStrokes(container);
    expect(strokes).toHaveLength(1);
    expect(sameColor(strokes[0] ?? null, '#EF4444')).toBeTruthy();
  });

  it('the budget reference line is a dashed grey line at the budget value', () => {
    const { container } = render(
      <CumulativeLineChart budget="500.00" days={UNDER_DAYS} />
    );
    const reference = container.querySelectorAll('.recharts-reference-line');
    expect(reference).toHaveLength(1);
    const line = reference[0]?.querySelector('line');
    expect(line).toBeTruthy();
    expect(sameColor(line?.getAttribute('stroke') ?? null, '#9CA3AF')).toBeTruthy();
    expect(line?.getAttribute('stroke-dasharray')).toBeTruthy();
  });

  it('a month with no days renders the empty state instead of a chart', () => {
    const { container } = render(
      <CumulativeLineChart budget="500.00" days={[]} />
    );
    expect(
      screen.getByRole('heading', { name: 'No spending this month' })
    ).toBeTruthy();
    expect(container.querySelector('svg.recharts-surface')).toBeNull();
  });

  it('the cumulative line chart is an accessible image named from its chart description', () => {
    render(<CumulativeLineChart budget="500.00" days={UNDER_DAYS} />);
    expect(
      screen.getByRole('img', { name: 'Cumulative spending line chart' })
    ).toBeTruthy();
  });
});

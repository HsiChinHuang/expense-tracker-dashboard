// AC5: WeeklyHeatmap tests (REQ-FE-073; t21).
//
// Seven frozen nodes. The component is a CUSTOM role="grid"/role="gridcell"
// div grid (deliberately not a charting-library chart), so every assertion
// is plain-DOM: cells, inline background colors, aria-labels, document
// order. Style assertions convert the pinned hex to the rgb(…) form jsdom
// reports (test files are the exempt coercion scope).

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WeeklyHeatmap } from './weekly_heatmap';
import type { HeatmapWeek } from './weekly_heatmap';

/** Convert an #RRGGBB literal to the rgb(…) form jsdom reports in styles. */
const rgb = (hex: string): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgb(${r}, ${g}, ${b})`;
};

const ZERO = rgb('#F3F4F6');
const SHADE_1 = rgb('#DBEAFE');
const SHADE_2 = rgb('#93C5FD');
const SHADE_3 = rgb('#3B82F6');
const SHADE_4 = rgb('#1E40AF');

const week = (week_start: string, amounts: string[]): HeatmapWeek => ({
  week_start,
  days: amounts.map((amount, index) => {
    const dayNumber = String(index + 1).padStart(2, '0');
    return { date: `${week_start.slice(0, 7)}-${dayNumber}`, amount };
  })
});

const cellColor = (element: HTMLElement): string =>
  element.style.backgroundColor.trim();

const allCells = (container: HTMLElement): HTMLElement[] =>
  Array.from(container.querySelectorAll('[role="gridcell"]')) as HTMLElement[];

describe('WeeklyHeatmap (ac5)', () => {
  it('the weekly heatmap is an accessible grid named from its chart description', () => {
    render(<WeeklyHeatmap max_amount="100.00" weeks={[week('2026-02-02', ['50.00', '0.00', '10.00', '25.00', '75.00', '100.00', '1.00'])]} />);
    const grid = screen.getByRole('grid', {
      name: 'Weekly spending heatmap grid'
    });
    expect(grid).toBeTruthy();
    expect(grid.querySelectorAll('[role="gridcell"]')).toHaveLength(7);
  });

  it('every day cell renders for missing days with the zero color', () => {
    const { container } = render(
      <WeeklyHeatmap
        max_amount="100.00"
        weeks={[week('2026-02-02', ['0.00', '40.00', '0.00', '0.00', '80.00', '0.00', '0.00'])]}
      />
    );
    const cells = allCells(container);
    // EVERY day of the window renders, missing days included.
    expect(cells).toHaveLength(7);
    [0, 2, 3, 5, 6].forEach((index) => {
      const cell = cells[index];
      expect(cell ? cellColor(cell) : '').toBe(ZERO);
    });
  });

  it('the cell color escalates with the amount against the window maximum', () => {
    const { container } = render(
      <WeeklyHeatmap
        max_amount="100.00"
        weeks={[week('2026-02-02', ['0.00', '20.00', '60.00', '90.00', '100.00', '10.00', '0.00'])]}
      />
    );
    const cells = allCells(container);
    const colorOf = (index: number): string => {
      const cell = cells[index];
      return cell ? cellColor(cell) : '';
    };
    expect(colorOf(0)).toBe(ZERO);
    expect(colorOf(1)).toBe(SHADE_1); // 20% of max -> lightest shade
    expect(colorOf(2)).toBe(SHADE_2); // 60% of max -> >= half
    expect(colorOf(3)).toBe(SHADE_3); // 90% of max -> >= three quarters
    expect(colorOf(4)).toBe(SHADE_4); // max itself -> darkest
  });

  it('a window whose maximum is zero renders every cell in the zero color', () => {
    const { container } = render(
      <WeeklyHeatmap
        max_amount="0.00"
        weeks={[
          week('2026-02-02', ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00']),
          week('2026-02-09', ['0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00'])
        ]}
      />
    );
    const cells = allCells(container);
    expect(cells).toHaveLength(14);
    cells.forEach((cell) => expect(cellColor(cell)).toBe(ZERO));
  });

  it('each cell exposes its date and amount to assistive technology', () => {
    const window: HeatmapWeek = {
      week_start: '2026-02-02',
      days: [
        { date: '2026-02-02', amount: '3.50' },
        { date: '2026-02-03', amount: '0.00' },
        { date: '2026-02-04', amount: '1.25' },
        { date: '2026-02-05', amount: '0.00' },
        { date: '2026-02-06', amount: '0.00' },
        { date: '2026-02-07', amount: '0.00' },
        { date: '2026-02-08', amount: '0.00' }
      ]
    };
    render(<WeeklyHeatmap max_amount="3.50" weeks={[window]} />);
    // Pinned aria-label form: `<date> $<amount>` (Q7 pins 2026-02-02 $3.50).
    expect(
      screen.getByRole('gridcell', { name: '2026-02-02 $3.50' })
    ).toBeTruthy();
    expect(
      screen.getByRole('gridcell', { name: '2026-02-03 $0.00' })
    ).toBeTruthy();
    expect(
      screen.getByRole('gridcell', { name: '2026-02-04 $1.25' })
    ).toBeTruthy();
  });

  it('an empty window renders the empty state instead of a grid', () => {
    const { container } = render(<WeeklyHeatmap max_amount="0.00" weeks={[]} />);
    expect(
      screen.getByRole('heading', { name: 'No activity in this window' })
    ).toBeTruthy();
    expect(container.querySelector('[role="grid"]')).toBeNull();
    expect(container.querySelector('[role="gridcell"]')).toBeNull();
  });

  it('a year boundary window renders its days in calendar order', () => {
    const december: HeatmapWeek = {
      week_start: '2025-12-29',
      days: [
        { date: '2025-12-29', amount: '1.00' },
        { date: '2025-12-30', amount: '0.00' },
        { date: '2025-12-31', amount: '2.00' },
        { date: '2026-01-01', amount: '0.00' },
        { date: '2026-01-02', amount: '3.00' },
        { date: '2026-01-03', amount: '0.00' },
        { date: '2026-01-04', amount: '0.00' }
      ]
    };
    const { container } = render(
      <WeeklyHeatmap max_amount="3.00" weeks={[december]} />
    );
    const dates = allCells(container).map(
      (cell) => cell.getAttribute('aria-label') ?? ''
    );
    expect(dates).toEqual([
      '2025-12-29 $1.00',
      '2025-12-30 $0.00',
      '2025-12-31 $2.00',
      '2026-01-01 $0.00',
      '2026-01-02 $3.00',
      '2026-01-03 $0.00',
      '2026-01-04 $0.00'
    ]);
    const ascending = [...dates].sort();
    expect(dates.map((label) => label.slice(0, 10))).toEqual(
      ascending.map((label) => label.slice(0, 10))
    );
  });
});

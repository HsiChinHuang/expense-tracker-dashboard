// AC2: CategoryPieChart tests (REQ-FE-070, REQ-PROD-033, REQ-FE-110; t21).
//
// Seven frozen nodes. PRESENTATIONAL component on plain data props: NO MSW
// handler is needed (setup.ts errors on unhandled requests, so any network
// call would surface as a failure). Assertions are DOM-observable: slice
// fills via the SVG scan helper, tooltip content via fireEvent, the pinned
// EmptyState heading via role queries.

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { CategoryPieChart } from './category_pie_chart';
import type { CategoryPieRow } from './category_pie_chart';

/**
 * SVG presentation attributes serialize VERBATIM in jsdom, so fills are
 * compared against the pinned hex literals case-insensitively.
 */
const sameColor = (actual: string | null, hex: string): boolean =>
  (actual ?? '').trim().toLowerCase() === hex.toLowerCase();

/** Pie-sector <path> fills in render order (sector groups only). */
const sliceFills = (container: HTMLElement): string[] =>
  Array.from(container.querySelectorAll('.recharts-pie-sector path')).map(
    (path) => (path.getAttribute('fill') ?? path.getAttribute('style') ?? '').trim()
  );

const row = (
  id: string,
  name: string,
  color: string,
  amount: string,
  percentage: number
): CategoryPieRow => ({
  category_id: id,
  category_name: name,
  color,
  amount,
  percentage
});

const THREE_ROWS: CategoryPieRow[] = [
  row('c1', 'Groceries', '#22C55E', '120.00', 40),
  row('c2', 'Rent', '#8B5CF6', '150.00', 50),
  row('c3', 'Fun', '#F59E0B', '30.00', 10)
];

const SEVEN_ROWS: CategoryPieRow[] = [
  row('c1', 'Groceries', '#22C55E', '100.00', 30),
  row('c2', 'Rent', '#8B5CF6', '90.00', 27),
  row('c3', 'Fun', '#F59E0B', '80.00', 24),
  row('c4', 'Transport', '#EF4444', '70.00', 21),
  row('c5', 'Health', '#06B6D4', '60.00', 18),
  row('c6', 'Utilities', '#A855F7', '50.00', 15),
  row('c7', 'Books', '#14B8A6', '0.10', 5)
];

/** Eight rows: the merged tail is 0.10 + 0.20 — the float-noise trap. */
const DECIMAL_TAIL_ROWS: CategoryPieRow[] = [
  ...SEVEN_ROWS,
  row('c8', 'Movies', '#F97316', '0.20', 4)
];

const SIX_ROWS = SEVEN_ROWS.slice(0, 6);

describe('CategoryPieChart (ac2)', () => {
  it('the pie chart is an accessible image named from its chart description', () => {
    render(<CategoryPieChart categories={THREE_ROWS} />);
    expect(
      screen.getByRole('img', { name: 'Spending by category pie chart' })
    ).toBeTruthy();
  });

  it('the pie chart renders one slice per category in the api colors', () => {
    const { container } = render(<CategoryPieChart categories={THREE_ROWS} />);
    const fills = sliceFills(container);
    const apiColors = ['#22C55E', '#8B5CF6', '#F59E0B'];
    apiColors.forEach((hex) => {
      expect(fills.filter((fill) => sameColor(fill, hex))).toHaveLength(1);
    });
    // One slice per row: exactly three pie-sector paths carry API colors.
    const apiColored = fills.filter((fill) =>
      apiColors.some((hex) => sameColor(fill, hex))
    );
    expect(apiColored).toHaveLength(3);
  });

  it('the pie slice tooltip shows the category name amount and percentage', () => {
    const { container } = render(<CategoryPieChart categories={THREE_ROWS} />);
    const sector = container.querySelectorAll('.recharts-pie-sector')[1];
    const target = sector?.querySelector('path') ?? sector;
    expect(target).toBeTruthy();
    fireEvent.mouseEnter(target as Element, { clientX: 50, clientY: 50 });
    fireEvent.mouseMove(target as Element, { clientX: 50, clientY: 50 });
    expect(screen.getAllByText('Rent').length).toBeGreaterThanOrEqual(1);
    // Amount renders VERBATIM from the API string, `$`-prefixed.
    expect(screen.getByText('$150.00')).toBeTruthy();
    expect(screen.getByText('50%')).toBeTruthy();
  });

  it('seven categories render six api slices plus one Other slice', () => {
    render(<CategoryPieChart categories={SEVEN_ROWS} />);
    // Exactly one legend entry carries the pinned `Other` label…
    const legendItems = screen
      .getAllByText('Other')
      .filter((entry) => entry.closest('.recharts-legend-item') !== null);
    expect(legendItems).toHaveLength(1);
    // …and the six API names survive as legend entries of their own.
    expect(screen.getAllByText('Groceries').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Utilities').length).toBeGreaterThanOrEqual(1);
    // The merged seventh category name is gone from the legend: the tail
    // collapsed into the single `Other` entry, not seven-plus-one slices.
    expect(screen.queryByText('Books')).toBeNull();
  });

  it('the Other slice amount is the decimal-safe sum of the merged tail', () => {
    const { container } = render(<CategoryPieChart categories={DECIMAL_TAIL_ROWS} />);
    const sectors = container.querySelectorAll('.recharts-pie-sector');
    // Eight rows merge to seven slices: the LAST is the `Other` slice.
    expect(sectors).toHaveLength(7);
    const otherSector = sectors[6];
    const target = otherSector?.querySelector('path') ?? otherSector;
    expect(target).toBeTruthy();
    fireEvent.mouseEnter(target as Element, { clientX: 50, clientY: 50 });
    fireEvent.mouseMove(target as Element, { clientX: 50, clientY: 50 });
    // 0.10 + 0.20 must render $0.30 — never 0.30000000000000004 float noise.
    expect(screen.getByText('$0.30')).toBeTruthy();
    expect(screen.queryByText(/\.\d{5,}/)).toBeNull();
  });

  it('exactly six categories render six slices with no Other slice', () => {
    render(<CategoryPieChart categories={SIX_ROWS} />);
    expect(screen.queryByText('Other')).toBeNull();
    expect(screen.getByText('Utilities')).toBeTruthy();
  });

  it('an empty category list renders the empty state instead of a chart', () => {
    const { container } = render(<CategoryPieChart categories={[]} />);
    expect(
      screen.getByRole('heading', { name: 'No expenses this month' })
    ).toBeTruthy();
    expect(container.querySelector('svg.recharts-surface')).toBeNull();
    expect(screen.queryByRole('img')).toBeNull();
  });
});

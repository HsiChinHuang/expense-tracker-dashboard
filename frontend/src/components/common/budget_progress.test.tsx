// AC4: BudgetProgress (REQ-FE-074, REQ-PROD-023 — t22). Five frozen nodes
// covering the three color thresholds (green < 80, yellow 80–100 INCLUSIVE
// at both ends, red > 100), the 100% width cap, and the null-percentage
// "No budget set" case. jsdom normalizes hex fills to rgb(), so the
// assertions use the normalized form (Q2).

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BudgetProgress } from './budget_progress';

/** Hex -> the rgb() form jsdom reports for inline styles. */
const rgb = (hex: string): string => {
  const body = hex.replace('#', '');
  const red = parseInt(body.slice(0, 2), 16);
  const green = parseInt(body.slice(2, 4), 16);
  const blue = parseInt(body.slice(4, 6), 16);
  return `rgb(${red}, ${green}, ${blue})`;
};

const renderProgress = (props: {
  percentage: number | null;
  total?: string;
  budget?: string;
  is_over_budget?: boolean;
}): void => {
  render(
    <BudgetProgress
      percentage={props.percentage}
      total={props.total ?? '125.50'}
      budget={props.budget ?? '2000.00'}
      is_over_budget={props.is_over_budget ?? false}
    />
  );
};

const fill = (): HTMLElement => screen.getByTestId('budget-progress-fill');

describe('BudgetProgress (ac4)', () => {
  it('a percentage under eighty renders the green fill below the cap', () => {
    renderProgress({ percentage: 6.3 });
    const track = screen.getByRole('progressbar');
    expect(track.getAttribute('aria-valuenow')).toBe('6.3');
    expect(fill().style.width).toBe('6.3%');
    expect(fill().style.backgroundColor).toBe(rgb('#22C55E'));
  });

  it('a percentage of exactly eighty renders the yellow fill', () => {
    renderProgress({ percentage: 80 });
    expect(fill().style.backgroundColor).toBe(rgb('#EAB308'));
    expect(fill().style.width).toBe('80%');
  });

  it('a percentage of exactly one hundred renders yellow at the full cap', () => {
    renderProgress({ percentage: 100 });
    expect(fill().style.backgroundColor).toBe(rgb('#EAB308'));
    expect(fill().style.width).toBe('100%');
  });

  it('an over budget percentage renders red with the width capped at one hundred', () => {
    renderProgress({ percentage: 133.7 });
    expect(fill().style.backgroundColor).toBe(rgb('#EF4444'));
    // The fill width is capped at the track even though the value is higher.
    expect(fill().style.width).toBe('100%');
    // The aria value reports the TRUE percentage, not the capped width.
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('133.7');
  });

  it('a null percentage renders no budget set with verbatim amounts and no bar', () => {
    renderProgress({ percentage: null, total: '125.50', budget: '0.00' });
    expect(screen.getByText('No budget set')).toBeTruthy();
    // Amounts are the API strings with a '$' prefix, verbatim (REQ-PROD-023).
    expect(screen.getByText('$125.50 of $0.00')).toBeTruthy();
    // Q3: no progressbar region and no fill element at all.
    expect(screen.queryByRole('progressbar')).toBeNull();
    expect(screen.queryByTestId('budget-progress-fill')).toBeNull();
  });
});

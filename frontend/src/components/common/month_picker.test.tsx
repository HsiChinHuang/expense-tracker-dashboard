// AC2: MonthPicker (REQ-FE-032, REQ-FE-062 header, REQ-FE-110 — t22).
// Three frozen nodes. The picker is driven by (and drives) the REAL
// MonthContext — never a stub — and every assertion is on rendered DOM.
// The expected month is computed test-side from the wall clock (merged
// month_context.test.tsx / budget_page.test.tsx precedent: no fake timers).

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MonthProvider, useMonth } from '../../context/month_context';
import { MonthPicker } from './month_picker';

/** Wall-clock YYYY-MM (the provider's own default, computed identically). */
const nowMonth = (): string => {
  const now = new Date();
  return `${String(now.getFullYear())}-${String(now.getMonth() + 1).padStart(2, '0')}`;
};

/** Shift a YYYY-MM by delta months (test-side integer math). */
const shiftMonth = (yearMonth: string, delta: number): string => {
  const parts = yearMonth.split('-');
  const index = Number(parts[0] ?? '0') * 12 + (Number(parts[1] ?? '0') - 1) + delta;
  const year = Math.floor(index / 12);
  const month = ((index % 12) + 12) % 12 + 1;
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}`;
};

/** "2026-10" -> "October 2026" (test-side lookup, mirrors the component). */
const humanLabel = (yearMonth: string): string => {
  const names = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];
  const parts = yearMonth.split('-');
  const name = names[Number(parts[1] ?? '0') - 1] ?? '';
  return `${name} ${parts[0] ?? ''}`;
};

/** Context probe: shows the shared month the picker must move. */
const MonthProbe = (): JSX.Element => {
  const { yearMonth } = useMonth();
  return <span data-testid="context-month">{yearMonth}</span>;
};

const renderPicker = (): void => {
  render(
    <MonthProvider>
      <MonthPicker />
      <MonthProbe />
    </MonthProvider>
  );
};

describe('MonthPicker (ac2)', () => {
  it('the month picker labels the context month in human form', () => {
    const expected = nowMonth();
    renderPicker();
    expect(screen.getByTestId('context-month').textContent).toBe(expected);
    expect(screen.getByTestId('month-picker-label').textContent).toBe(humanLabel(expected));
  });

  it('the step buttons are keyboard-reachable controls with accessible names', () => {
    renderPicker();
    const previous = screen.getByRole('button', { name: 'Previous month' });
    const next = screen.getByRole('button', { name: 'Next month' });
    // Native <button> elements: keyboard-focusable with accessible names.
    expect(previous.tagName).toBe('BUTTON');
    expect(next.tagName).toBe('BUTTON');
    expect(previous.getAttribute('aria-label')).toBe('Previous month');
    expect(next.getAttribute('aria-label')).toBe('Next month');
  });

  it('stepping the picker moves the shared context month by one', () => {
    const start = nowMonth();
    renderPicker();
    expect(screen.getByTestId('context-month').textContent).toBe(start);
    fireEvent.click(screen.getByRole('button', { name: 'Next month' }));
    const forward = shiftMonth(start, 1);
    expect(screen.getByTestId('context-month').textContent).toBe(forward);
    expect(screen.getByTestId('month-picker-label').textContent).toBe(humanLabel(forward));
    // Two steps back lands one month behind the start (year boundary safe:
    // the math is the shared context's, asserted at the context + label).
    fireEvent.click(screen.getByRole('button', { name: 'Previous month' }));
    fireEvent.click(screen.getByRole('button', { name: 'Previous month' }));
    const back = shiftMonth(start, -1);
    expect(screen.getByTestId('context-month').textContent).toBe(back);
    expect(screen.getByTestId('month-picker-label').textContent).toBe(humanLabel(back));
  });
});

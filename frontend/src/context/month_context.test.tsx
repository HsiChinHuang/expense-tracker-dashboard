// AC1: MonthContext tests (REQ-FE-030 / REQ-FE-032, t20).
//
// Six frozen nodes (docs/issues/t20.md inventory). The default is proven by
// PATTERN only — a clock-derived exact value is flaky across month
// boundaries (t18 precedent, groom REWORD). The month-math contract is
// pinned by the year-boundary, shape-preservation and rapid-click nodes;
// every assertion is made THROUGH A CONSUMER (context output, never code
// reading), and two consumers prove the value is shared.

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MonthProvider, useMonth } from './month_context';

/** Consumer A: renders the raw value so the shape is asserted as text. */
const MonthText = (): JSX.Element => {
  const { yearMonth } = useMonth();
  return <span data-testid="month">{yearMonth}</span>;
};

/** Consumer B: a SEPARATE reader proving one provider value is shared. */
const MonthEcho = (): JSX.Element => {
  const { yearMonth } = useMonth();
  return <span data-testid="echo">{yearMonth}</span>;
};

/** Controls exercise the context surface exactly as a MonthPicker would. */
const Controls = (): JSX.Element => {
  const { prevMonth, nextMonth, setYearMonth } = useMonth();
  return (
    <>
      <button type="button" onClick={prevMonth}>
        prev
      </button>
      <button type="button" onClick={nextMonth}>
        next
      </button>
      <button type="button" onClick={() => setYearMonth('2026-03')}>
        set-2026-03
      </button>
      <button type="button" onClick={() => setYearMonth('2026-12')}>
        set-2026-12
      </button>
      <button type="button" onClick={() => setYearMonth('2027-01')}>
        set-2027-01
      </button>
    </>
  );
};

const renderScene = (): void => {
  render(
    <MonthProvider>
      <MonthText />
      <MonthEcho />
      <Controls />
    </MonthProvider>
  );
};

const month = (): string | null => screen.getByTestId('month').textContent;

describe('MonthContext (ac1)', () => {
  it('yearMonth defaults to a well-formed YYYY-MM string', () => {
    renderScene();
    const value = month() ?? '';
    // Pattern-only proof (a clock-exact assertion is flaky at month
    // boundaries); the month is a four-digit year and a 01..12 month.
    expect(value).toMatch(/^\d{4}-(0[1-9]|1[0-2])$/);
    // The default is the wall-clock month, not an arbitrary constant.
    const now = new Date();
    expect(value.slice(0, 4)).toBe(String(now.getFullYear()));
  });

  it('setYearMonth updates the value seen by every consumer', () => {
    renderScene();
    fireEvent.click(screen.getByText('set-2026-03'));
    // BOTH independent consumers observe the new value (single source).
    expect(month()).toBe('2026-03');
    expect(screen.getByTestId('echo').textContent).toBe('2026-03');
  });

  it('nextMonth walks December forward to January of the next year', () => {
    renderScene();
    fireEvent.click(screen.getByText('set-2026-12'));
    fireEvent.click(screen.getByText('next'));
    expect(month()).toBe('2027-01');
  });

  it('prevMonth walks January back to December of the previous year', () => {
    renderScene();
    fireEvent.click(screen.getByText('set-2027-01'));
    fireEvent.click(screen.getByText('prev'));
    expect(month()).toBe('2026-12');
  });

  it('prevMonth and nextMonth never mutate the YYYY-MM shape', () => {
    renderScene();
    fireEvent.click(screen.getByText('set-2026-03'));
    for (const step of ['next', 'prev', 'prev', 'next']) {
      fireEvent.click(screen.getByText(step));
      expect(month() ?? '').toMatch(/^\d{4}-(0[1-9]|1[0-2])$/);
    }
    // Four inverse steps return to the start: no drift, no shape change.
    expect(month()).toBe('2026-03');
  });

  it('rapid nextMonth clicks land on the month six steps ahead', () => {
    renderScene();
    fireEvent.click(screen.getByText('set-2026-03'));
    for (let click = 0; click < 6; click += 1) {
      fireEvent.click(screen.getByText('next'));
    }
    // Six steps from 2026-03 is 2026-09 (functional updates compose even
    // when React batches the clicks into one render pass).
    expect(month()).toBe('2026-09');
    expect(screen.getByTestId('echo').textContent).toBe('2026-09');
  });
});

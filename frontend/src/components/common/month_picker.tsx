// MonthPicker — the shared, accessible month stepper (REQ-FE-062 header,
// REQ-FE-032, REQ-FE-110; t22 ac2).
//
// A NEW component (t22 Constraints): the merged budget page keeps its own
// inline picker, nothing is refactored. The component is PRESENTATIONAL and
// stdlib-only — it reads the single shared selection from MonthContext via
// `useMonth` and steps it through the context's own `prevMonth` /
// `nextMonth` callbacks, so every month-driven dashboard query moves with
// it. It performs NO data fetching and imports no router, so it renders in
// any tree that carries a MonthProvider.
//
// The human label is a Record lookup keyed by the MM text of the `YYYY-MM`
// (Q7): no numeric coercion, no Date, no Intl, no date-fns anywhere.

import { useMonth } from '../../context/month_context';

/** Full month names indexed by the MM text of a `YYYY-MM` key. */
const MONTH_NAMES: Record<string, string> = {
  '01': 'January',
  '02': 'February',
  '03': 'March',
  '04': 'April',
  '05': 'May',
  '06': 'June',
  '07': 'July',
  '08': 'August',
  '09': 'September',
  '10': 'October',
  '11': 'November',
  '12': 'December'
};

/** "2026-10" -> "October 2026"; an unknown MM falls back to the raw key. */
const humanMonthLabel = (yearMonth: string): string => {
  const parts = yearMonth.split('-');
  const year = parts[0] ?? '';
  const month = parts[1] ?? '';
  const name = MONTH_NAMES[month];
  return name === undefined ? yearMonth : `${name} ${year}`;
};

/** Prev/next stepper plus the accessible label for the context month. */
export const MonthPicker = (): JSX.Element => {
  const { yearMonth, prevMonth, nextMonth } = useMonth();
  return (
    <div className="flex items-center gap-2" data-testid="month-picker">
      <button
        type="button"
        aria-label="Previous month"
        onClick={prevMonth}
        className="rounded border border-slate-300 px-2 py-1 text-slate-700"
      >
        &larr;
      </button>
      <span aria-live="polite" data-testid="month-picker-label">
        {humanMonthLabel(yearMonth)}
      </span>
      <button
        type="button"
        aria-label="Next month"
        onClick={nextMonth}
        className="rounded border border-slate-300 px-2 py-1 text-slate-700"
      >
        &rarr;
      </button>
    </div>
  );
};

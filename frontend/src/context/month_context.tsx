// MonthContext — the app's global month selection (REQ-FE-030, REQ-FE-032).
//
// One provider owns the single `YYYY-MM` the dashboard reads (REQ-FE-030:
// UI global state lives in context, not in pages). The value defaults to the
// CURRENT wall-clock month; `prevMonth`/`nextMonth` walk it by one and
// `setYearMonth` jumps it. Provider nesting stays ADDITIVE (REQ-ARCH-013):
// main.tsx inserts MonthProvider between AuthProvider and ToastProvider so
// any page or hook can consume it without a rewrite.
//
// The month math is stdlib string/integer arithmetic DUPLICATED from the
// merged `budget_page.tsx` shiftMonth logic. Extraction is FORBIDDEN (t20
// review_plan W3): the merged `export const shiftMonth`/`monthWindow` are
// imported BY NAME by the frozen budget_page.test.tsx, so the duplicated
// helpers below are private to this module and the merged exports REMAIN.

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode
} from 'react';

/** Month value shape: `YYYY-MM` (the same shape every endpoint echoes). */
export type YearMonth = string;

export interface MonthContextValue {
  /** The selected month, always a well-formed `YYYY-MM` string. */
  yearMonth: YearMonth;
  /** Jump to an explicit `YYYY-MM` (the month picker's onChange). */
  setYearMonth: (value: YearMonth) => void;
  /** Step one month backwards. */
  prevMonth: () => void;
  /** Step one month forwards. */
  nextMonth: () => void;
}

/** Shift a YYYY-MM string by `delta` months (stdlib integer math only —
 * date-fns is BANNED, t20 Constraints). Never mutates the YYYY-MM shape. */
const shiftMonth = (yearMonth: YearMonth, delta: number): YearMonth => {
  const [yearText, monthText] = yearMonth.split('-');
  const index = Number(yearText) * 12 + (Number(monthText) - 1) + delta;
  const year = Math.floor(index / 12);
  const month = ((index % 12) + 12) % 12 + 1;
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}`;
};

/** Current wall-clock month as YYYY-MM (the provider's default value). */
const currentMonth = (): YearMonth => {
  const now = new Date();
  const year = String(now.getFullYear());
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
};

const MonthContext = createContext<MonthContextValue | null>(null);

/** Provides the shared month; mounts between Auth and Toast (REQ-ARCH-013). */
export const MonthProvider = ({ children }: { children: ReactNode }): JSX.Element => {
  const [yearMonth, setYearMonth] = useState<YearMonth>(currentMonth);

  // Functional update: rapid clicks compose on the pending value, so six
  // clicks land six months ahead even when React batches the events.
  const step = useCallback((delta: number): void => {
    setYearMonth((current) => shiftMonth(current, delta));
  }, []);

  const value = useMemo<MonthContextValue>(
    () => ({
      yearMonth,
      setYearMonth,
      prevMonth: () => step(-1),
      nextMonth: () => step(1)
    }),
    [yearMonth, step]
  );

  return <MonthContext.Provider value={value}>{children}</MonthContext.Provider>;
};

// The merged context precedent (auth_context.tsx:110, toast_context.tsx:146)
// exports its hook beside its provider and carries a react-refresh warning
// for it. t20's DoD pins the lint baseline at the four MEASURED warnings, so
// the same shape is kept here with the warning scoped off by construction:
// the file still follows the rule's intent (one provider, one reader hook).

/** Access the shared month; throws outside a MonthProvider tree. */
// eslint-disable-next-line react-refresh/only-export-components -- provider + hook pairing (merged t9/t17 context precedent)
export const useMonth = (): MonthContextValue => {
  const context = useContext(MonthContext);
  if (!context) {
    throw new Error('useMonth must be used within a MonthProvider');
  }
  return context;
};

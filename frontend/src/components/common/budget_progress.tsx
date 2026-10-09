// BudgetProgress — the fifth "chart" (REQ-FE-074, REQ-PROD-023; t22 ac4).
//
// A pure div progress bar, deliberately NOT a charting-library component:
// it renders the month's spend against the budget with the frozen color
// thresholds — green `#22C55E` under 80%, yellow `#EAB308` at 80–100%
// INCLUSIVE, red `#EF4444` above 100% (or when the API flags the month over
// budget) — and the fill width is capped at 100% so an over-budget month
// still fits its track.
//
// The `percentage` arrives as the API's JSON number and is used DIRECTLY as
// a number (Q2): this module performs NO numeric coercion and NO percent
// math of its own, and money renders from the API strings verbatim (a
// backtick '$' prefix, nothing else). A null percentage (no budget set)
// renders the "No budget set" affordance plus the verbatim amounts and NO
// progressbar region at all (Q3).

/** Frozen Chapter2 §2.5.4 threshold colors. */
const GREEN = '#22C55E';
const YELLOW = '#EAB308';
const RED = '#EF4444';

/** Track cap: the fill never exceeds 100% of its track width. */
const WIDTH_CAP = 100;

export interface BudgetProgressProps {
  /** Percent of budget spent — the API JSON number, or null (no budget). */
  percentage: number | null;
  /** Month total, 2-decimal string, rendered VERBATIM. */
  total: string;
  /** Month budget, 2-decimal string, rendered VERBATIM. */
  budget: string;
  /** The API's over-budget flag (drives red alongside percentage > 100). */
  is_over_budget: boolean;
}

/** Threshold color for a numeric percentage (Q2 boundaries, frozen). */
const fillColor = (percentage: number, isOverBudget: boolean): string => {
  if (isOverBudget || percentage > WIDTH_CAP) {
    return RED;
  }
  if (percentage >= 80) {
    return YELLOW;
  }
  return GREEN;
};

export const BudgetProgress = ({
  percentage,
  total,
  budget,
  is_over_budget
}: BudgetProgressProps): JSX.Element => {
  if (percentage === null) {
    return (
      <div data-testid="budget-progress">
        <p className="text-sm text-slate-500">No budget set</p>
        <p className="text-sm text-slate-700">{`$${total} of $${budget}`}</p>
      </div>
    );
  }

  const width = percentage > WIDTH_CAP ? WIDTH_CAP : percentage;
  const color = fillColor(percentage, is_over_budget);

  return (
    <div data-testid="budget-progress">
      <p className="text-sm text-slate-700">{`$${total} of $${budget}`}</p>
      <div
        role="progressbar"
        aria-label="Budget usage"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percentage}
        className="h-3 w-full rounded bg-slate-200"
        data-testid="budget-progress-track"
      >
        <div
          className="h-3 rounded"
          style={{ width: `${width}%`, backgroundColor: color }}
          data-testid="budget-progress-fill"
        />
      </div>
    </div>
  );
};

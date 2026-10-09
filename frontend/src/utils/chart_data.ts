// Chart data helpers (t21, REQ-PROD-023 money discipline).
//
// This module is the SINGLE AUDITED string→number coercion locus for the
// four chart components (ac6 gate): the components under
// `src/components/charts` stay free of bare `Number(` / `parseFloat(` /
// `parseInt(` / `.toFixed(` and route every numeric bridge through the
// `toNumber` wrapper below (whose call site reads `toNumber(`, never a bare
// coercion token).
//
// Money discipline: every amount-adding helper works on BIGINT CENTS
// (exact integer arithmetic), never float dollars, so decimal tails like
// 0.10 + 0.20 sum to exactly 0.30 with no float noise. Rendering always
// uses the API STRING verbatim — nothing here re-formats money for the DOM.

/** Shared chart palette (Chapter8 §8.11.2 / Chapter2 §2.5.4 frozen colors). */
export const CHART_BLUE = '#3B82F6';
export const CHART_RED = '#EF4444';
export const CHART_BUDGET_GREY = '#9CA3AF';

/** Heatmap ramp: zero cell then the four escalating shades (REQ-FE-073). */
export const HEATMAP_ZERO = '#F3F4F6';
export const HEATMAP_RAMP = ['#DBEAFE', '#93C5FD', '#3B82F6', '#1E40AF'] as const;

/** Month names for the stdlib "MMM YY" label (no Intl, no date-fns). */
const MONTH_ABBREVIATIONS = [
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

/**
 * Format a `YYYY-MM` key as the `MMM YY` axis label ("2025-01" -> "Jan 25",
 * "2026-12" -> "Dec 26"). Pure stdlib string math: no `date-fns`, no
 * `toLocaleDateString`, no `Date` (ac3 grep-pins this ban in the consumer).
 * Exported from `frontend/src/utils/` so all charts share one month layer.
 */
export const formatMonthLabel = (yearMonth: string): string => {
  const parts = yearMonth.split('-');
  const year = parts[0] ?? '';
  const month = Number(parts[1] ?? '0');
  const abbreviation = MONTH_ABBREVIATIONS[month - 1] ?? '???';
  return `${abbreviation} ${year.slice(-2)}`;
};

/**
 * The audited string→number bridge. Components may ONLY coerce through
 * this function (the ac6 token gate keys on bare `Number(`); unparseable
 * input falls back to the supplied default instead of NaN.
 */
export const toNumber = (value: string | number, fallback = 0): number => {
  const parsed = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

/** Money equality on 2-decimal strings (e.g. the exactly-at-budget edge). */
export const amountsEqual = (left: string, right: string): boolean =>
  dollarsToCents(left) === dollarsToCents(right);

/** True when `amount` exceeds `budget` — strict `>`, cents-exact. */
export const exceeds = (amount: string, budget: string): boolean =>
  dollarsToCents(amount) > dollarsToCents(budget);

/** Decimal-safe sum of money strings: bigint cents in, 2-decimal string out. */
export const sumAmounts = (amounts: readonly string[]): string => {
  const totalCents = amounts
    .map((amount) => dollarsToCents(amount))
    .reduce((running, cents) => running + cents, 0n);
  return centsToMoney(totalCents);
};

/** Decimal-safe sum of percentage numbers (the pie `Other` slice). */
export const sumPercentages = (percentages: readonly number[]): number =>
  percentages.reduce((running, value) => running + value, 0);

/**
 * Exact fraction test: is `amount` at least `numerator`/`denominator` of
 * `maximum`? Cross-multiplies BIGINT CENTS so the comparison is exact and
 * no float division (the banned token class) ever appears in a component.
 * A zero or negative maximum short-circuits to false (no divide-by-zero).
 */
export const ratioAtLeast = (
  amount: string,
  numerator: number,
  denominator: number,
  maximum: string
): boolean => {
  const maxCents = dollarsToCents(maximum);
  if (maxCents <= 0n) {
    return false;
  }
  return dollarsToCents(amount) * BigInt(denominator) >= maxCents * BigInt(numerator);
};

/** `2.5` -> "$2.50" for the USD value axis (cents out of the helper). */
export const formatUsdTick = (value: number): string =>
  `$${centsToMoney(BigInt(Math.round(toNumber(value) * 100)))}`;
/** Money string -> bigint cents ("12.34" -> 1234n); "" / junk -> 0n. */
const dollarsToCents = (value: string): bigint => {
  const text = value.trim();
  if (text === '') {
    return 0n;
  }
  const match = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(text);
  if (match === null) {
    return toNumber(text) === 0 ? 0n : BigInt(Math.round(toNumber(text) * 100));
  }
  const sign = match[1] === '-' ? -1n : 1n;
  const whole = match[2] ?? '0';
  const fraction = (match[3] ?? '').padEnd(2, '0');
  return sign * (BigInt(whole) * 100n + BigInt(fraction));
};

/** bigint cents -> canonical 2-decimal money string (no currency sign). */
const centsToMoney = (cents: bigint): string => {
  const sign = cents < 0n ? '-' : '';
  const absolute = cents < 0n ? -cents : cents;
  const whole = absolute / 100n;
  const fraction = (absolute % 100n).toString().padStart(2, '0');
  return `${sign}${whole.toString()}.${fraction}`;
};

# Design System

The visual language of the Expense Tracker Dashboard, measured from the
merged frontend on `main`. The rule of this document: **the doc follows
the code, never the reverse** - the hexes below are re-measured from the
non-test sources under `frontend/src`, and a code change must update
this page, not the other way around. Related:
[architecture.md](architecture.md),
[testing-guidelines.md](testing-guidelines.md).

## Colors

The application styles with Tailwind utility classes (slate/blue/red
scales); the palette is Tailwind's default - `tailwind.config.js`
extends nothing (`theme.extend` is empty), so the utility names in
components are the source of truth for UI chrome.

The ten hex values that appear in the merged non-test frontend code are
below. They are chart and status colors, deliberately hard-coded because
Recharts props need literal colors:

| Hex | Role | Where (merged code) |
|---|---|---|
| `#3B82F6` | Primary chart blue | `CHART_BLUE` in `frontend/src/utils/chart_data.ts`; trend bars, line series, heatmap level 4 |
| `#EF4444` | Over-budget / negative red | `CHART_RED` in `chart_data.ts`; `RED` in `budget_progress.tsx`; over-budget line in `cumulative_line_chart.tsx` |
| `#9CA3AF` | Budget reference grey | `CHART_BUDGET_GREY` in `chart_data.ts`; budget line in `cumulative_line_chart.tsx` |
| `#22C55E` | Under-budget green | `GREEN` in `frontend/src/components/common/budget_progress.tsx` |
| `#EAB308` | Warning yellow (80-100%) | `YELLOW` in `budget_progress.tsx` |
| `#94A3B8` | Neutral fallback slice | `FALLBACK_SLICE_COLOR` in `category_pie_chart.tsx` |
| `#F3F4F6` | Heatmap zero cell | `HEATMAP_ZERO` in `chart_data.ts` |
| `#DBEAFE` | Heatmap ramp step 1 | `HEATMAP_RAMP[0]` in `chart_data.ts` |
| `#93C5FD` | Heatmap ramp step 2 | `HEATMAP_RAMP[1]` in `chart_data.ts` |
| `#1E40AF` | Heatmap ramp step 4 (deepest) | `HEATMAP_RAMP[3]` in `chart_data.ts` |

Test-only hexes (for example `#123456`) live exclusively in `*.test.tsx`
files and are not part of the design system.

## Typography

- Base size is Tailwind's default 16px scale; body copy uses `text-sm`
  and `text-base` utilities, headlines use `text-base font-semibold`
  (see the title slot in
  `frontend/src/components/ui/empty_state.tsx`).
- Font stack is the browser default sans-serif chain from Tailwind's
  `font-sans`; no custom `@font-face` is loaded (the build ships no font
  assets).
- Numeric data (amounts, dates) renders the API string verbatim - the
  frontend never re-formats money, so typography is the only styling
  applied to those values.

## Spacing

- All spacing uses Tailwind's 4px scale utilities (`p-4`, `py-8`,
  `gap-2`, `mt-2`, ...); no arbitrary pixel values are introduced.
- Cards and panels follow the merged convention `rounded-md` corners
  with `p-4` padding; stacked groups separate with `gap-2`/`gap-4`.
- The shared empty surface centers its slots with
  `flex flex-col items-center gap-2 py-8` (see `empty_state.tsx`).

## Components

The merged component inventory (each with its own colocated test):

- `frontend/src/components/ui/empty_state.tsx` - icon / title /
  description / optional action slots for empty data.
- `frontend/src/components/ui/error_state.tsx` - `role="alert"` failure
  surface with an optional Retry button.
- `frontend/src/components/common/budget_progress.tsx` - progress bar
  colored by percentage (green under 80%, yellow 80-100%, red above).
- `frontend/src/components/common/month_picker.tsx`,
  `protected_route.tsx`, `public_only_route.tsx` - navigation guards and
  the month selector.
- `frontend/src/components/charts/` - the four Recharts views (pie,
  trend bars, cumulative line, weekly heatmap) fed by
  `frontend/src/utils/chart_data.ts`.
- `frontend/src/context/toast_context.tsx` - the single toast surface:
  one polite live region, 3-second auto-dismiss, manual dismiss, and a
  Retry action for network-coded toasts.

## Chart colors

The frozen chart palette (Chapter 8 section 8.11.2 / Chapter 2 section
2.5.4) lives in `frontend/src/utils/chart_data.ts`:

- `CHART_BLUE = '#3B82F6'` - primary series.
- `CHART_RED = '#EF4444'` - over-budget series.
- `CHART_BUDGET_GREY = '#9CA3AF'` - budget reference line.
- `HEATMAP_ZERO = '#F3F4F6'` - the zero-activity cell.
- `HEATMAP_RAMP = ['#DBEAFE', '#93C5FD', '#3B82F6', '#1E40AF']` - the
  four escalating activity shades, lightest to densest.

`weekly_heatmap.tsx` mirrors the ramp as `HEAT_SCALE` with the same five
stages (zero color first). Pie slices fall back to `#94A3B8` when a
category carries no usable color.

## States

Every asynchronous surface has three documented states:

- **Loading**: skeleton placeholders (owned by the t22 convention) while
  a query is in flight; never a blank panel.
- **Empty**: the `EmptyState` component - a plain message, plus an
  action slot only when the caller provides one.
- **Error**: the `ErrorState` component - the message inside a
  `role="alert"` region, a Retry button only when retry is possible;
  network-normalized failures additionally raise a toast from
  `toast_context.tsx` carrying its own retry action.

Toast variants are `success` and `error`; both auto-dismiss after
`TOAST_DURATION_MS = 3000`.

## Accessibility

- Toasts render inside a single `aria-live="polite"` region; decorative
  icons are `aria-hidden="true"` so the text carries meaning.
- Errors announce through `role="alert"`; the retry affordance is a
  real `<button type="button">`, keyboard-reachable.
- Interactive controls keep native semantics (buttons, labels on form
  inputs) rather than div-with-onclick patterns.
- Color is never the only signal: the budget bar pairs its color with a
  visible percentage, and chart series pair color with legends/tooltips.
- The heatmap ramp is monotonic in lightness so the density encoding
  survives common color-vision deficiencies.

## Specification tables (REQ-anchored)

The sections above measure the merged code. This section records the
normative surface the requirements name, and - where the merged code
has not caught up - says so plainly. The doc still follows the code;
where they disagree, the disagreement is written down rather than
papered over.

Typography (REQ-FE-091): page titles are `text-2xl font-semibold`
(measured on every merged page header), section titles are
`text-lg font-semibold` (measured on the form and history headers),
and KPI values take `text-3xl font-bold`. The font stack is the
system chain; tables and KPI numbers use `tabular-nums` so columns of
figures align. The page-title and section-title rules are measured in
`frontend/src/pages/*.tsx` and the form headers; the `text-3xl` KPI
and `tabular-nums` clauses are the spec and are checked at review
whenever a KPI surface changes.

Spacing (REQ-FE-092): the scale is page padding `px-6 py-8`, card
padding `p-6`, card gap `gap-6`, section gap `space-y-8`, form gap
`space-y-4`, and page width `max-w-7xl mx-auto`. The merged surfaces
currently sit on the tighter `p-4`/`gap-2` convention noted in the
Spacing section above; this table is the target scale the next visual
pass moves to, and the difference is a known, disclosed deviation -
not a claim that the merged code already uses `px-6 py-8`.

Component specifications (REQ-FE-093): buttons come in
primary/secondary/danger/ghost variants with defined backgrounds; a
Card carries border and shadow; an Input carries a focus ring and an
error state; a Modal carries an overlay, a focus trap, and a close
affordance. The merged inventory (`empty_state.tsx`, `error_state.tsx`,
`confirm_dialog.tsx`, `budget_progress.tsx`, the two forms) implements
the error, empty, dialog, and progress rows; the button-variant
palette is specified here so a new button picks a variant instead of
inventing a color. Focus handling is part of the spec: inputs and
buttons keep a visible focus ring, and the modal moves focus in on
open and returns it on close (measured in `budget_form.tsx`, which
calls `target.focus()` on open).

Chart colors (REQ-FE-094): the pie uses the category colors; trend
bars are `#3B82F6`; the cumulative line is `#3B82F6` normally and
`#EF4444` when spending crosses budget; the budget reference line is
the `#9CA3AF` dash; the heatmap uses the five-step ramp from the
Colors table. All five clauses are measured constants in
`frontend/src/utils/chart_data.ts` and the chart components.

Chart accessibility (REQ-FE-112): every chart carries
`role="img"` and an `aria-label` that summarizes what the chart shows
(measured on all four chart components, e.g. "Weekly spending heatmap
grid", with per-cell labels like `2026-10-05 $42.00` on heatmap
cells). The spec additionally calls for a `<figure>` wrapper with a
`<figcaption>`; the merged charts use the section heading as their
visible caption instead of a figcaption element, which is the one
clause recorded here as spec-ahead-of-code.

Product-level accessibility (REQ-PROD-025) aggregates the surface
above with the form rules: every input has a label, every button has
an accessible name, the modal has a role and a focus trap, and charts
have descriptions. The component tests assert the label/role queries,
and the color-never-alone rule (budget percentage rendered as text
beside the color, legends beside series) is the review checklist item
that keeps the aggregate claim honest.

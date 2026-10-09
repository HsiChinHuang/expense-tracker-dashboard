// EmptyState — the shared empty-data surface (REQ-FE-101, t20 ac5).
//
// The component half deferred from phase_3 by the t18 groom ruling Q8: t20
// creates it with its OWN test file, and NO merged page imports it (t21/t22
// consume it). Slots per the requirement: an icon, a title, a description
// and an ACTION slot that renders only when the caller provides one — an
// empty state without an action stays a plain message.
//
// Merged pages keep their inline `<p>` / role="status" conventions untouched
// (t20 Constraints: additive only).

import type { ReactNode } from 'react';

export interface EmptyStateProps {
  /** Decorative icon slot (rendered aria-hidden: the text carries meaning). */
  icon?: ReactNode;
  /** Headline naming what is missing. */
  title: string;
  /** Optional supporting copy. */
  description?: string;
  /** Optional action control; rendered ONLY when provided. */
  action?: ReactNode;
}

/** Renders the icon/title/description slots plus an optional action. */
export const EmptyState = ({
  icon,
  title,
  description,
  action
}: EmptyStateProps): JSX.Element => (
  <div className="flex flex-col items-center gap-2 py-8 text-center">
    {icon ? (
      <span aria-hidden="true" data-testid="empty-state-icon">
        {icon}
      </span>
    ) : null}
    <h3 className="text-base font-semibold">{title}</h3>
    {description ? <p className="text-sm text-slate-500">{description}</p> : null}
    {action ? <div data-testid="empty-state-action">{action}</div> : null}
  </div>
);

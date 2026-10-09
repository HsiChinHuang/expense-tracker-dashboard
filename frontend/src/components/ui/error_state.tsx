// ErrorState — the shared failure surface (REQ-FE-102, t20 ac5).
//
// The retry half deferred from phase_3 by the t18 groom ruling Q8. The
// message renders inside an accessible role="alert" region (the merged
// pages' inline convention, now as a component) and a Retry button invokes
// the caller's onRetry callback. The retry affordance renders ONLY when
// onRetry is provided: a caller that cannot retry gets the message alone.
//
// NOT created here: loading_indicator.tsx (t22 ac3 owns skeletons — the
// explicit negative leg of this issue). No merged page imports this
// component yet; its inline role="alert" markup stays untouched.

export interface ErrorStateProps {
  /** The human-readable failure message shown in the alert region. */
  message: string;
  /** Invoked by the Retry button; omit to render NO retry affordance. */
  onRetry?: () => void;
}

/** Alert-region error message with an optional retry affordance. */
export const ErrorState = ({ message, onRetry }: ErrorStateProps): JSX.Element => (
  <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-4">
    <p className="text-sm text-red-700">{message}</p>
    {onRetry ? (
      <button
        type="button"
        onClick={onRetry}
        className="mt-2 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white"
      >
        Retry
      </button>
    ) : null}
  </div>
);

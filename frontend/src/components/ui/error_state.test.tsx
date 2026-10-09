// AC5: ErrorState component tests (REQ-FE-102, t20).
//
// Three frozen nodes. The message must live in an accessible role="alert"
// region (the merged pages' inline convention, now a component), the Retry
// button invokes the caller's onRetry, and omitting onRetry removes the
// retry affordance entirely (a caller that cannot retry gets the message
// alone — no dead button).

import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { ErrorState } from './error_state';

describe('ErrorState (ac5)', () => {
  it('the error state renders the message in an accessible alert region', () => {
    render(<ErrorState message="Could not load the dashboard." />);
    const alert = screen.getByRole('alert');
    expect(alert.textContent).toContain('Could not load the dashboard.');
  });

  it('the error state retry button invokes the onRetry callback', () => {
    let retries = 0;
    render(
      <ErrorState
        message="Could not reach the server."
        onRetry={() => {
          retries += 1;
        }}
      />
    );
    const alert = screen.getByRole('alert');
    expect(alert.textContent).toContain('Could not reach the server.');
    const retry = screen.getByRole('button', { name: 'Retry' });
    fireEvent.click(retry);
    fireEvent.click(retry);
    // Every click reaches the callback (the caller refetches per click).
    expect(retries).toBe(2);
  });

  it('the error state renders without the retry affordance when onRetry is omitted', () => {
    render(<ErrorState message="Something went wrong." />);
    expect(screen.getByRole('alert').textContent).toContain('Something went wrong.');
    // No onRetry -> no retry control anywhere in the tree.
    expect(screen.queryByRole('button')).toBeNull();
    expect(screen.queryByText('Retry')).toBeNull();
  });
});

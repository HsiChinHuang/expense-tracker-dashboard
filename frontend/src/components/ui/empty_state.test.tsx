// AC5: EmptyState component tests (REQ-FE-101, t20).
//
// Two frozen nodes. The action slot is the contract's sharp edge: it must
// render ONLY when the caller provides one, so an action-less empty state
// stays a plain message with no stray control in the accessibility tree.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from './empty_state';

describe('EmptyState (ac5)', () => {
  it('the empty state renders the icon title and description slots', () => {
    render(
      <EmptyState
        icon={<span>icon-marker</span>}
        title="No expenses yet"
        description="Add your first expense to start tracking."
      />
    );
    expect(screen.getByText('icon-marker')).toBeTruthy();
    expect(screen.getByTestId('empty-state-icon').textContent).toBe('icon-marker');
    expect(screen.getByRole('heading', { level: 3 }).textContent).toBe('No expenses yet');
    expect(screen.getByText('Add your first expense to start tracking.')).toBeTruthy();
    // No action was provided: the action slot stays out of the DOM.
    expect(screen.queryByTestId('empty-state-action')).toBeNull();
  });

  it('the empty state renders the action control only when provided', () => {
    const withoutAction = render(<EmptyState title="No transactions" />);
    expect(withoutAction.queryByRole('button')).toBeNull();
    expect(withoutAction.queryByTestId('empty-state-action')).toBeNull();
    withoutAction.unmount();

    render(
      <EmptyState
        title="No transactions"
        action={
          <button type="button">Add expense</button>
        }
      />
    );
    expect(screen.getByTestId('empty-state-action')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Add expense' })).toBeTruthy();
  });
});

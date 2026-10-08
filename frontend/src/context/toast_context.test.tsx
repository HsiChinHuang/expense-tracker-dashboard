// AC1: ToastProvider contract (REQ-FE-033, t17 — t9 carry-forward).
// Frozen titles (docs/issues/t17.md inventory, 4 nodes): live region,
// 3-second auto-dismiss, manual dismiss inside the window, and the
// NETWORK_ERROR retry action invoking the caller-supplied callback.
//
// user-event is NOT a dependency (no new deps) — fireEvent + fake timers
// are the merged t9/t16 interaction precedent.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import type { ReactNode } from 'react';
import { ToastProvider, TOAST_DURATION_MS, useToast } from './toast_context';

/** Consumer component that pushes toasts through the context API. */
const Pusher = ({
  message,
  variant,
  code,
  retry
}: {
  message: string;
  variant?: 'success' | 'error';
  code?: string;
  retry?: () => void;
}): JSX.Element => {
  const { showToast } = useToast();
  return (
    <button
      type="button"
      onClick={() => {
        showToast(
          message,
          variant,
          code !== undefined || retry !== undefined
            ? {
                ...(code !== undefined ? { code } : {}),
                ...(retry !== undefined ? { retry } : {})
              }
            : undefined
        );
      }}
    >
      push
    </button>
  );
};

const Provider = ({ children }: { children: ReactNode }): JSX.Element => (
  <ToastProvider>{children}</ToastProvider>
);

/** The single live region every toast renders into. */
const liveRegion = (): HTMLElement | null => document.querySelector('[aria-live="polite"]');

/** Presence check that never collides with page-level role="status" nodes. */
const toastText = (message: string): HTMLElement | null => screen.queryByText(message);

describe('ToastProvider', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('showToast renders the message in an accessible live region', () => {
    render(
      <Provider>
        <Pusher message="Expense created" />
      </Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'push' }));
    const region = liveRegion();
    expect(region).not.toBeNull();
    expect(region?.getAttribute('aria-live')).toBe('polite');
    expect(region?.textContent).toContain('Expense created');
  });

  it('toasts auto-dismiss after three seconds', () => {
    render(
      <Provider>
        <Pusher message="Expense created" />
      </Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'push' }));
    expect(toastText('Expense created')).not.toBeNull();
    // Still visible just BEFORE the three-second window closes.
    act(() => {
      vi.advanceTimersByTime(TOAST_DURATION_MS - 500);
    });
    expect(toastText('Expense created')).not.toBeNull();
    // Gone once the window closes (the dismiss timer fired inside act()).
    act(() => {
      vi.advanceTimersByTime(600);
    });
    expect(toastText('Expense created')).toBeNull();
  });

  it('the dismiss button removes the toast before the auto-dismiss window', () => {
    render(
      <Provider>
        <Pusher message="Expense created" />
      </Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'push' }));
    expect(toastText('Expense created')).not.toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss notification' }));
    expect(toastText('Expense created')).toBeNull();
    // The timer was cleared: advancing past the window changes nothing.
    act(() => {
      vi.advanceTimersByTime(TOAST_DURATION_MS + 1000);
    });
    expect(toastText('Expense created')).toBeNull();
  });

  it('a network-error toast surfaces a retry action that invokes the retry callback', () => {
    const retrySpy = vi.fn();
    render(
      <Provider>
        <Pusher
          message="Could not reach the server. Please try again."
          variant="error"
          code="NETWORK_ERROR"
          retry={retrySpy}
        />
      </Provider>
    );
    fireEvent.click(screen.getByRole('button', { name: 'push' }));
    expect(toastText('Could not reach the server. Please try again.')).not.toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    expect(retrySpy).toHaveBeenCalledTimes(1);
  });
});

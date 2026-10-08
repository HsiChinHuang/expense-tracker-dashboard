// ToastContext — the app's only toast surface (REQ-FE-033, t17).
//
// Pays the t9 carry-forward: a request that normalizes to NETWORK_ERROR
// (merged t9 interceptor) can be surfaced as a toast carrying a retry
// action. The showToast signature is builder-chosen within the contract:
// `showToast(message, variant?, options?)` where options carry the
// optional `code` (enables the retry affordance for NETWORK_ERROR) and
// the `retry` callback the retry button invokes.
//
// Behavior pinned by the frozen titles: every toast renders inside ONE
// accessible live region (aria-live="polite"), auto-dismisses after
// THREE seconds, can be dismissed manually before that window, and a
// network-code toast exposes a Retry button that invokes the callback.

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode
} from 'react';

/** How long a toast stays on screen (REQ-FE-033: three seconds). */
export const TOAST_DURATION_MS = 3000;

export type ToastVariant = 'success' | 'error';

export interface Toast {
  id: number;
  message: string;
  variant: ToastVariant;
  /** Normalized error code (e.g. NETWORK_ERROR) — drives the retry affordance. */
  code?: string;
  /** Invoked by the retry action; present only when the toast is retryable. */
  retry?: () => void;
}

export interface ShowToastOptions {
  code?: string;
  retry?: () => void;
}

interface ToastContextValue {
  toasts: Toast[];
  showToast: (message: string, variant?: ToastVariant, options?: ShowToastOptions) => void;
  dismissToast: (id: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let nextToastId = 1;

export const ToastProvider = ({ children }: { children: ReactNode }): JSX.Element => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const dismissToast = useCallback((id: number): void => {
    const timer = timers.current.get(id);
    if (timer !== undefined) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (message: string, variant: ToastVariant = 'success', options?: ShowToastOptions): void => {
      const id = nextToastId;
      nextToastId += 1;
      const toast: Toast = {
        id,
        message,
        variant,
        ...(options?.code !== undefined ? { code: options.code } : {}),
        ...(options?.retry !== undefined ? { retry: options.retry } : {})
      };
      setToasts((current) => [...current, toast]);
      const timer = setTimeout(() => {
        dismissToast(id);
      }, TOAST_DURATION_MS);
      timers.current.set(id, timer);
    },
    [dismissToast]
  );

  // Any timer still pending when the provider unmounts must not fire later.
  useEffect(
    () => () => {
      for (const timer of timers.current.values()) {
        clearTimeout(timer);
      }
      timers.current.clear();
    },
    []
  );

  const value = useMemo<ToastContextValue>(
    () => ({ toasts, showToast, dismissToast }),
    [toasts, showToast, dismissToast]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div aria-live="polite" aria-label="Notifications" className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`rounded p-3 text-sm shadow ${
              toast.variant === 'error' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'
            }`}
          >
            <span>{toast.message}</span>
            {toast.code === 'NETWORK_ERROR' && toast.retry ? (
              <button
                type="button"
                className="ml-2 underline"
                onClick={() => {
                  toast.retry?.();
                }}
              >
                Retry
              </button>
            ) : null}
            <button
              type="button"
              aria-label="Dismiss notification"
              className="ml-2 font-bold"
              onClick={() => {
                dismissToast(toast.id);
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

/** Access the toast surface; throws outside the provider. */
export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

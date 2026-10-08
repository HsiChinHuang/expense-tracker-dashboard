// ConfirmDialog — confirmation gate for destructive actions (REQ-FE-103, t17).
//
// A controlled presentational dialog: the parent owns open/close state, so
// opening it performs NO side effect (the delete handler is only reached
// through onConfirm). role="dialog" + aria-modal, focus moves into the
// dialog on open and returns to the previously focused element on close
// (REQ-FE-111).

import { useEffect, useRef, type ReactNode } from 'react';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  onConfirm: () => void;
  onCancel: () => void;
  children?: ReactNode;
}

export const ConfirmDialog = ({
  open,
  title,
  onConfirm,
  onCancel,
  children
}: ConfirmDialogProps): JSX.Element | null => {
  const confirmRef = useRef<HTMLButtonElement | null>(null);
  const restoreRef = useRef<Element | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }
    restoreRef.current = document.activeElement;
    confirmRef.current?.focus();
    return () => {
      const target = restoreRef.current;
      restoreRef.current = null;
      if (target instanceof HTMLElement) {
        target.focus();
      }
    };
  }, [open]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/50">
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-full max-w-sm rounded bg-white p-4 shadow"
      >
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        {children ? <div className="mt-2 text-sm text-slate-600">{children}</div> : null}
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            className="rounded border border-slate-300 px-3 py-1"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            type="button"
            ref={confirmRef}
            className="rounded bg-red-600 px-3 py-1 text-white"
            onClick={onConfirm}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

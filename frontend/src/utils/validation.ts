// Form validation helpers (t9, REQ-TECH-006).
//
// @hookform/resolvers is deliberately NOT a dependency (t9 adds only
// react-hook-form and zod), so the zod -> React Hook Form bridge is
// hand-rolled here, together with the mapping from normalized backend
// errors onto named form fields.

import { z } from 'zod';
import type { FieldErrors, FieldValues, Resolver } from 'react-hook-form';
import type { ApiError } from '../api/client';

/** Create an RHF resolver that validates the form values with a zod schema. */
export const zodResolver =
  <S extends z.ZodTypeAny>(schema: S): Resolver<z.infer<S>> =>
  async (values: FieldValues): Promise<{ values: z.infer<S>; errors: FieldErrors }> => {
    const result = schema.safeParse(values);
    if (result.success) {
      return { values: result.data, errors: {} };
    }
    const errors: FieldErrors = {};
    for (const issue of result.error.issues) {
      const path = issue.path.join('.');
      if (path && !errors[path]) {
        errors[path] = { type: 'validate', message: issue.message };
      }
    }
    return { values: {} as z.infer<S>, errors };
  };

/**
 * Map a normalized backend error onto form fields.
 *
 * A 409/422 body carries `{code, field}`; the message is placed on the
 * named field when the backend names one, otherwise it is exposed as a
 * `root` error so the page can render it inline.
 */
export const applyApiErrors = (
  error: ApiError,
  setError: (name: string, error: { type: string; message: string }) => void
): void => {
  if (error.field) {
    setError(error.field, { type: 'server', message: error.message });
  } else {
    setError('root', { type: 'server', message: error.message });
  }
};

// ---------------------------------------------------------------------------
// Expense form schemas (REQ-FE-080, t17).
//
// Money stays a STRING end to end (REQ-PROD-023): the rules below are a
// string regex plus a string-space numeric comparison. No parseFloat /
// parseInt / toFixed anywhere — the magnitude bound is compared by
// shifting the decimal point at most twice and comparing integers.
// ---------------------------------------------------------------------------

/** Upper bound as an integer number of cents: 9,999,999,999.99 -> 999999999999. */
const MAX_AMOUNT_CENTS = 999_999_999_999;

/** Positive decimal string with at most two decimal places. */
const AMOUNT_PATTERN = /^\d+(?:\.\d{1,2})?$/;

/** Compare against the max without floats: scale the string by 100 exactly. */
const withinAmountMax = (value: string): boolean => {
  const [whole, fraction = ''] = value.split('.');
  const centsText = `${whole ?? ''}${(fraction + '00').slice(0, 2)}`;
  const digits = centsText.replace(/^0+(?=\d)/, '');
  const maxText = String(MAX_AMOUNT_CENTS);
  if (digits.length !== maxText.length) {
    return digits.length < maxText.length;
  }
  return digits <= maxText;
};

/** Amount field: required, positive, <= 2 decimals, <= 9999999999.99. */
export const amountSchema = z
  .string()
  .min(1, 'Amount is required')
  .refine((value) => AMOUNT_PATTERN.test(value), {
    message: 'Amount must be a positive number with at most 2 decimals'
  })
  .refine(withinAmountMax, {
    message: 'Amount must be 9999999999.99 or less'
  });

/** Full expense create/edit form schema (date required, note optional). */
export const expenseFormSchema = z.object({
  amount: amountSchema,
  category_id: z.string().min(1, 'Category is required'),
  date: z
    .string()
    .min(1, 'Date is required')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Enter a valid date'),
  note: z.string().max(500, 'Note must be 500 characters or fewer').optional()
});

/** Values shape handled by the expense form (strings only — money stays text). */
export type ExpenseFormValues = z.infer<typeof expenseFormSchema>;

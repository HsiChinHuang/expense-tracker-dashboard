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

// CategoryForm — the INLINE category create form (REQ-FE-065/080/082, t18).
//
// Rendered directly on the categories page (no modal, no focus trap — the
// page owns focus here, per the groom's drop of the survey's modal nodes).
// It reuses the merged t9 helpers: hand-rolled zodResolver + applyApiErrors
// and mode:'onChange' (t17 precedent). A backend {detail, code, field}
// error maps onto the named field; a field the form does not own (the
// delete-time in-use 409 carries field='category_id', Q5) is NOT pushed
// here — the page renders it as a root/row-level role="alert".
//
// The icon field is optional end to end: an empty icon input OMITS the
// `icon` key from the payload entirely (Q7), which is what the frozen
// create-payload node asserts at the handler.
//
// t74 colour/icon UX: the colour row is a CONTROL TRIO — the text field
// (exact label `Color`, unchanged) plus a native <input type="color">
// carrying ONLY an aria-label `Color picker` (never a second `Color`
// label, so the frozen page-test getByLabelText('Color') stays exact),
// plus a live swatch (data-testid `category-color-swatch`). The field is
// PREFILLED with the neutral #94A3B8 — the charts' FALLBACK_SLICE_COLOR
// and one of the ten documented design-system hexes (the tests[212]
// exact-10 gate forbids any eleventh hex) — and the post-create reset
// returns to that same default. Frontend validation stays ADVISORY:
// HEX_COLOR_PATTERN in backend/app/schemas/category.py plus the DB CHECK
// ck_categories_color_format remain the final gate; the form only
// renders an extra human-readable hint beside the merged zod message.

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import type { ApiError } from '../../api/client';
import { applyApiErrors, categoryFormSchema, zodResolver } from '../../utils/validation';
import type { CategoryFormValues } from '../../utils/validation';

export interface CategorySubmitResult {
  ok: boolean;
  error?: ApiError;
}

/** Pinned neutral prefill (t74 Option A): the chart fallback hex, already
 * one of the ten documented design-system values. */
const DEFAULT_COLOR = '#94A3B8';

/** Client-side ADVISORY mirror of the backend HEX_COLOR_PATTERN
 * (backend/app/schemas/category.py) — byte-identical, never a replacement. */
const HEX_COLOR_RE = /^#[0-9A-Fa-f]{6}$/;

/** Pinned human-readable format hint (rendered by the FORM, not zod). */
const COLOR_FORMAT_HINT = 'Use # plus six hex digits, for example #22C55E';

interface CategoryFormProps {
  onSubmit: (values: CategoryFormValues) => Promise<CategorySubmitResult>;
}

export const CategoryForm = ({ onSubmit }: CategoryFormProps): JSX.Element => {
  const {
    register: bindField,
    handleSubmit,
    setError,
    reset,
    setValue,
    formState: { errors, isSubmitting }
  } = useForm<CategoryFormValues>({
    resolver: zodResolver(categoryFormSchema),
    mode: 'onChange',
    defaultValues: { name: '', color: DEFAULT_COLOR, icon: '' }
  });

  // Uncontrolled text value mirrored for the swatch and the picker sync.
  const [colorDraft, setColorDraft] = useState<string>(DEFAULT_COLOR);

  // Advisory-only sync: picker -> text always; text -> picker ONLY when the
  // typed value is valid, so an invalid typed value never overwrites the
  // picker (jsdom resets an out-of-range type=color value to the default).
  const pickerColor = HEX_COLOR_RE.test(colorDraft) ? colorDraft : DEFAULT_COLOR;

  const submit = async (values: CategoryFormValues): Promise<void> => {
    const result = await onSubmit(values);
    if (result.ok) {
      reset({ name: '', color: DEFAULT_COLOR, icon: '' });
      setColorDraft(DEFAULT_COLOR);
      return;
    }
    if (result.error) {
      applyApiErrors(result.error, (name, error) => {
        setError(name as keyof CategoryFormValues, error);
      });
    }
  };

  return (
    <form className="mt-4 max-w-md space-y-3" noValidate onSubmit={handleSubmit(submit)}>
      <div>
        <label className="block text-sm text-slate-700" htmlFor="category-name">
          Name
        </label>
        <input
          className="w-full rounded border border-slate-300 p-2"
          id="category-name"
          autoComplete="off"
          {...bindField('name')}
        />
        {errors.name ? (
          <p className="mt-1 text-sm text-red-600" id="category-name-error">
            {errors.name.message}
          </p>
        ) : null}
      </div>
      <div>
        <label className="block text-sm text-slate-700" htmlFor="category-color">
          Color
        </label>
        <div className="flex items-center gap-2">
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="category-color"
            autoComplete="off"
            placeholder="#RRGGBB, e.g. #22C55E"
            {...bindField('color', {
              onChange: (event) => setColorDraft(event.target.value)
            })}
          />
          <input
            type="color"
            aria-label="Color picker"
            className="h-9 w-10 rounded border border-slate-300 p-1"
            value={pickerColor}
            onChange={(event) => {
              setColorDraft(event.target.value);
              // setValue is imperative and does NOT fire the registered
              // onChange, so the onChange resolver revalidates on the next
              // change/event — the page test's change-driven 409 flow stays
              // byte-identical.
              void setValue('color', event.target.value, { shouldValidate: false });
            }}
          />
          <span
            aria-hidden="true"
            data-testid="category-color-swatch"
            className={`inline-block h-8 w-8 rounded border border-slate-300 bg-[${colorDraft || DEFAULT_COLOR}]`}
          />
        </div>
        {errors.color ? (
          <p className="mt-1 text-sm text-red-600">
            {errors.color.message} - {COLOR_FORMAT_HINT}
          </p>
        ) : null}
      </div>
      <div>
        <label className="block text-sm text-slate-700" htmlFor="category-icon">
          Icon (optional)
        </label>
        <p className="text-xs text-slate-500">(optional, e.g. utensils)</p>
        <input
          className="w-full rounded border border-slate-300 p-2"
          id="category-icon"
          autoComplete="off"
          {...bindField('icon')}
        />
        {errors.icon ? (
          <p className="mt-1 text-sm text-red-600">{errors.icon.message}</p>
        ) : null}
      </div>
      {errors.root ? (
        <p className="text-sm text-red-600" role="alert">
          {errors.root.message}
        </p>
      ) : null}
      <button
        type="submit"
        className="rounded bg-slate-800 px-3 py-1 text-white disabled:opacity-50"
        disabled={isSubmitting}
      >
        Add category
      </button>
    </form>
  );
};

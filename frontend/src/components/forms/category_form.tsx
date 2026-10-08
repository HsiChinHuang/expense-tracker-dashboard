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

import { useForm } from 'react-hook-form';
import type { ApiError } from '../../api/client';
import { applyApiErrors, categoryFormSchema, zodResolver } from '../../utils/validation';
import type { CategoryFormValues } from '../../utils/validation';

export interface CategorySubmitResult {
  ok: boolean;
  error?: ApiError;
}

interface CategoryFormProps {
  onSubmit: (values: CategoryFormValues) => Promise<CategorySubmitResult>;
}

export const CategoryForm = ({ onSubmit }: CategoryFormProps): JSX.Element => {
  const {
    register: bindField,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<CategoryFormValues>({
    resolver: zodResolver(categoryFormSchema),
    mode: 'onChange',
    defaultValues: { name: '', color: '', icon: '' }
  });

  const submit = async (values: CategoryFormValues): Promise<void> => {
    const result = await onSubmit(values);
    if (result.ok) {
      reset({ name: '', color: '', icon: '' });
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
        <input
          className="w-full rounded border border-slate-300 p-2"
          id="category-color"
          autoComplete="off"
          {...bindField('color')}
        />
        {errors.color ? (
          <p className="mt-1 text-sm text-red-600">{errors.color.message}</p>
        ) : null}
      </div>
      <div>
        <label className="block text-sm text-slate-700" htmlFor="category-icon">
          Icon (optional)
        </label>
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

// CategoriesPage — system + custom category management (REQ-FE-065,
// REQ-PROD-013/034, REQ-FE-100/101/102/103, REQ-FE-015, REQ-SEC-033, t18).
//
// Data access goes through the merged t16 hooks ONLY (REQ-ARCH-012):
// use_categories for the list, use_create_category and use_delete_category
// for the mutations (each invalidates ["categories"], which refreshes the
// mounted list). The list is split client-side into a SYSTEM section and a
// CUSTOM section.
//
// REQ-SEC-033: system rows carry NO delete affordance at all — not a
// disabled button, an ABSENT one (the merged backend only exposes
// GET/POST/DELETE /api/v1/categories; there is no rename/update endpoint,
// so there is also no edit control to render). Custom rows delete through
// the ConfirmDialog. The in-use 409 carries field='category_id', which is
// not a field on this page's form, so it surfaces as a root-level
// role="alert" message with the verbatim backend text (Q5), never on the
// name field. Loading/error/empty states are the inline t17 conventions
// (role="status" / role="alert" + Retry / plain <p>) — no state components
// exist yet (Q8).

import { useEffect, useState } from 'react';
import { use_categories, use_create_category, use_delete_category } from '../hooks/use_categories';
import { CategoryForm } from '../components/forms/category_form';
import type { CategorySubmitResult } from '../components/forms/category_form';
import { ConfirmDialog } from '../components/ui/confirm_dialog';
import { useToast } from '../context/toast_context';
import { toApiError } from '../api/client';
import type { Category } from '../api/categories';
import type { CategoryFormValues } from '../utils/validation';

export const CategoriesPage = (): JSX.Element => {
  const { showToast } = useToast();
  const list = use_categories();
  const create = use_create_category();
  const remove = use_delete_category();

  const [pendingDelete, setPendingDelete] = useState<Category | null>(null);
  const [inUseMessage, setInUseMessage] = useState<string | null>(null);

  useEffect(() => {
    document.title = 'Categories';
  }, []);

  const categories = list.data?.categories ?? [];
  const systemRows = categories.filter((category) => category.is_system);
  const customRows = categories.filter((category) => !category.is_system);

  const submitCreate = async (
    values: CategoryFormValues
  ): Promise<CategorySubmitResult> => {
    try {
      await create.mutateAsync({
        name: values.name,
        color: values.color,
        // Empty icon input -> the key is OMITTED entirely (Q7).
        ...(values.icon !== undefined && values.icon !== '' ? { icon: values.icon } : {})
      });
      showToast('Category created', 'success');
      return { ok: true };
    } catch (error) {
      const apiError = toApiError(error);
      showToast(apiError.message, 'error');
      return { ok: false, error: apiError };
    }
  };

  const confirmDelete = async (): Promise<void> => {
    if (!pendingDelete) {
      return;
    }
    const target = pendingDelete;
    setPendingDelete(null);
    try {
      await remove.mutateAsync(target.id);
      showToast('Category deleted', 'success');
    } catch (error) {
      const apiError = toApiError(error);
      // Q5: the in-use 409 names field='category_id', which this page's
      // form does not own — surface it as a root-level alert, not on the
      // name field.
      setInUseMessage(apiError.message);
      showToast(apiError.message, 'error');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold text-slate-900">Categories</h1>

      {list.isPending ? (
        <p role="status" className="mt-4 text-slate-600">
          Loading categories…
        </p>
      ) : null}

      {list.isError ? (
        <div role="alert" className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">
          <p>Could not load categories. The server may be unreachable.</p>
          <button
            type="button"
            className="mt-2 rounded border border-red-300 px-2 py-1"
            onClick={() => {
              void list.refetch();
            }}
          >
            Retry
          </button>
        </div>
      ) : null}

      {!list.isPending && !list.isError ? (
        <>
          <section className="mt-4">
            <h2 className="text-lg font-semibold text-slate-900">System categories</h2>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {systemRows.map((category) => (
                <li key={category.id} data-testid="system-category-row">
                  <span
                    aria-hidden="true"
                    className="mr-2 inline-block h-3 w-3 rounded"
                    style={{ backgroundColor: category.color }}
                  />
                  {category.name}
                </li>
              ))}
            </ul>
          </section>

          <section className="mt-8">
            <h2 className="text-lg font-semibold text-slate-900">Custom categories</h2>
            {inUseMessage ? (
              <p role="alert" className="mt-2 text-sm text-red-700">
                {inUseMessage}
              </p>
            ) : null}
            {customRows.length === 0 ? (
              <p className="mt-2 text-slate-600">
                No custom categories yet. Add your first category.
              </p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm text-slate-700">
                {customRows.map((category) => (
                  <li key={category.id} data-testid="custom-category-row">
                    <span
                      aria-hidden="true"
                      className="mr-2 inline-block h-3 w-3 rounded"
                      style={{ backgroundColor: category.color }}
                    />
                    {category.name}
                    <button
                      type="button"
                      className="ml-2 underline text-red-700"
                      onClick={() => {
                        setInUseMessage(null);
                        setPendingDelete(category);
                      }}
                    >
                      Delete {category.name}
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <h3 className="mt-6 text-base font-semibold text-slate-900">Add a category</h3>
            <CategoryForm onSubmit={submitCreate} />
          </section>
        </>
      ) : null}

      <ConfirmDialog
        open={pendingDelete !== null}
        title="Delete category"
        onConfirm={() => {
          void confirmDelete();
        }}
        onCancel={() => {
          setPendingDelete(null);
        }}
      >
        This removes the category from your custom categories.
      </ConfirmDialog>
    </div>
  );
};

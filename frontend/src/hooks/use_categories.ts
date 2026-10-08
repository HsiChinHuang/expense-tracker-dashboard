/* eslint-disable react-hooks/rules-of-hooks -- the project coding standard
pins snake_case hook names (use_categories); eslint-plugin-react-hooks only
recognizes usePascalCase, so the recognition false-positive is scoped off
here while the Rules of Hooks are still followed by construction. */
// Category data hooks (REQ-FE-034/035, REQ-FE-051, t16).
//
// Category mutations invalidate ["categories"] ONLY — deliberately NOT
// ["dashboard"] (the REQ-FE-051 asymmetry: expenses/budgets feed the
// dashboard, categories do not). The negative control is pinned as an
// observable test in use_categories.test.tsx.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createCategory,
  deleteCategory,
  listCategories,
  type CreateCategoryPayload
} from '../api/categories';
import { queryKeys } from '../api/query_keys';

/** Category list query backed by the object-wrapper endpoint. */
export const use_categories = () =>
  useQuery({
    queryKey: queryKeys.categories.all,
    queryFn: () => listCategories()
  });

/** Create mutation: invalidates ["categories"] only (REQ-FE-051). */
export const use_create_category = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateCategoryPayload) => createCategory(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['categories'] });
    }
  });
};

/** Delete mutation: invalidates ["categories"] only (REQ-FE-051). */
export const use_delete_category = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCategory(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['categories'] });
    }
  });
};

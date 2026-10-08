// Typed category API module (REQ-FE-042/043, t11 contract mirror).
//
// One function per Chapter 7 §7.4 endpoint, 1:1. All calls go through the
// shared `api` instance from `./client` (REQ-ARCH-070). Money-adjacent and
// timestamp fields are plain strings end-to-end — this layer performs no
// numeric coercion (REQ-PROD-023).

import { api } from './client';

/** Public category representation — exactly the six backend fields (REQ-API-030). */
export interface Category {
  id: string;
  name: string;
  color: string;
  icon: string | null;
  is_system: boolean;
  created_at: string;
}

/** Response body for GET /api/v1/categories — the contractual object wrapper. */
export interface CategoryList {
  categories: Category[];
}

/** Payload for POST /api/v1/categories (name 1-100, HEX color, optional icon). */
export interface CreateCategoryPayload {
  name: string;
  color: string;
  icon?: string;
}

/** List the caller's visible categories (system block first). */
export const listCategories = async (): Promise<CategoryList> => {
  const response = await api.get<CategoryList>('/api/v1/categories');
  return response.data;
};

/** Create a custom category for the caller. */
export const createCategory = async (
  payload: CreateCategoryPayload
): Promise<Category> => {
  const response = await api.post<Category>('/api/v1/categories', payload);
  return response.data;
};

/** Delete one of the caller's custom categories (system rows 403 upstream). */
export const deleteCategory = async (id: string): Promise<void> => {
  await api.delete(`/api/v1/categories/${id}`);
};

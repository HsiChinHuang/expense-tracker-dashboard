// t74: CategoryForm colour/icon UX (REQ-FE-065/080/082). Colocated form
// test — the admitted new file (P6 in the pin table): the prefill/reset
// lifecycle legs cannot be observed from the page test without driving the
// whole create round-trip, and the budget_form/expense_form colocated
// precedent applies. The form is presentational: the harness owns
// submission through the onSubmit contract, so no QueryClient or network
// is needed here (the merged handlers.ts stays untouched).
//
// Frozen node titles (5): the color control trio, the neutral default +
// reset, the human-readable format hint, the icon example hint, and the
// Q7 empty-icon key omission re-proved at the FORM level.

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { CategoryForm } from './category_form';
import type { CategorySubmitResult } from './category_form';
import type { CategoryFormValues } from '../../utils/validation';

/** Capture harness: records the submitted values, always succeeds. */
const captureSubmit = (
  received: { current: CategoryFormValues | null }
): ((values: CategoryFormValues) => Promise<CategorySubmitResult>) => {
  return async (values: CategoryFormValues): Promise<CategorySubmitResult> => {
    received.current = values;
    return { ok: true };
  };
};

const colorInput = (): HTMLInputElement =>
  screen.getByLabelText('Color') as HTMLInputElement;

const iconInput = (): HTMLInputElement =>
  screen.getByLabelText('Icon (optional)') as HTMLInputElement;

const pickerInput = (): HTMLInputElement =>
  screen.getByLabelText('Color picker') as HTMLInputElement;

const swatch = (): HTMLElement => screen.getByTestId('category-color-swatch');

const submitButton = (): HTMLButtonElement =>
  screen.getByRole('button', { name: 'Add category' }) as HTMLButtonElement;

describe('CategoryForm color UX (t74)', () => {
  it('the color field offers a picker, an example placeholder and a live swatch that follows the value', () => {
    const received = { current: null as CategoryFormValues | null };
    render(<CategoryForm onSubmit={captureSubmit(received)} />);
    // The text field keeps the exact `Color` label and gains the example.
    expect(colorInput().getAttribute('placeholder')).toBe('#RRGGBB, e.g. #22C55E');
    // The native picker is named `Color picker` (never a second `Color`).
    const picker = pickerInput();
    expect(picker.getAttribute('type')).toBe('color');
    // The live swatch follows the text value.
    expect(swatch().className).toContain('bg-[#94A3B8]');
    fireEvent.change(colorInput(), { target: { value: '#123456' } });
    expect(swatch().className).toContain('bg-[#123456]');
    // Sync leg picker -> text: the picker drives the text field.
    fireEvent.change(picker, { target: { value: '#00ff00' } });
    expect(colorInput().value).toBe('#00ff00');
  });

  it('the color field starts at the neutral default and a successful create resets to it', async () => {
    const received = { current: null as CategoryFormValues | null };
    render(<CategoryForm onSubmit={captureSubmit(received)} />);
    // Prefilled with the pinned neutral #94A3B8 (Option A: the chart
    // fallback hex, already one of the ten documented values).
    expect(colorInput().value).toBe('#94A3B8');
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New' } });
    fireEvent.change(colorInput(), { target: { value: '#123456' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(received.current).not.toBeNull();
    });
    // The typed value is what reaches onSubmit.
    expect(received.current?.color).toBe('#123456');
    // The reset leg returns to the DEFAULT, not to empty.
    await waitFor(() => {
      expect(colorInput().value).toBe('#94A3B8');
    });
    expect(swatch().className).toContain('bg-[#94A3B8]');
  });

  it('an invalid color shows a human-readable format hint', async () => {
    const received = { current: null as CategoryFormValues | null };
    const submit = vi.fn(captureSubmit(received));
    render(<CategoryForm onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New' } });
    fireEvent.change(colorInput(), { target: { value: 'green' } });
    // The merged zod message plus the pinned human-readable hint render.
    await waitFor(() => {
      expect(screen.queryByText(/Use # plus six hex digits, for example #22C55E/)).not.toBeNull();
    });
    expect(document.body.textContent).toContain('Color must be a 6-digit HEX value');
    // Advisory leg: the invalid value is blocked client side.
    expect(submit).not.toHaveBeenCalled();
    // An invalid typed value never overwrites the picker (advisory-only
    // sync): the picker keeps a valid hex, never the invalid text. The
    // native picker reports LOWERCASE hex — left verbatim (card constraint:
    // no casing "fix" on user input).
    expect(pickerInput().value.toLowerCase()).toBe('#94a3b8');
  });
});

describe('CategoryForm icon UX (t74)', () => {
  it('the icon field shows the optional-utensils example hint', () => {
    const received = { current: null as CategoryFormValues | null };
    render(<CategoryForm onSubmit={captureSubmit(received)} />);
    // The example lives in a SEPARATE hint element; the visible label
    // stays byte-identical `Icon (optional)` and the query stays unique.
    expect(screen.getByText('(optional, e.g. utensils)')).toBeTruthy();
    expect(screen.getAllByLabelText('Icon (optional)')).toHaveLength(1);
    expect(iconInput().id).toBe('category-icon');
  });

  it('an empty icon input omits the icon key from the submitted values', async () => {
    const received = { current: null as CategoryFormValues | null };
    // Harness mirrors the page's pinned Q7 spread
    // (categories_page.tsx: `...(values.icon !== '' ? { icon } : {})`),
    // so the omission contract is re-proved at the FORM-values level.
    const posted: { current: Record<string, unknown> | null } = { current: null };
    const submit = async (values: CategoryFormValues): Promise<CategorySubmitResult> => {
      posted.current = {
        name: values.name,
        color: values.color,
        ...(values.icon !== undefined && values.icon !== '' ? { icon: values.icon } : {})
      };
      received.current = values;
      return { ok: true };
    };
    render(<CategoryForm onSubmit={submit} />);
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New' } });
    // Icon left EMPTY: the payload OMITS the icon key entirely (Q7).
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect(posted.current).not.toBeNull();
    });
    expect('icon' in (posted.current as Record<string, unknown>)).toBe(false);
    // A typed icon DOES travel into the payload (name refilled: the
    // successful create reset the form back to its defaults).
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New' } });
    fireEvent.change(iconInput(), { target: { value: 'utensils' } });
    fireEvent.click(submitButton());
    await waitFor(() => {
      expect((posted.current as Record<string, unknown>).icon).toBe('utensils');
    });
  });
});

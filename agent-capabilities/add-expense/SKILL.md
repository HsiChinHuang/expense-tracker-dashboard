---
name: add-expense
description: Record a new expense by validating the amount first and confirming the result.
---

# add-expense

## When to Use

Use this skill when the user asks to record, log, or add a new expense
with an amount, a category, and a date.

## Steps

1. Validate the amount with the `validate_amount` hook: it must be a positive number with at most two decimal places; if it fails, stop and ask the user to correct the value.
2. Call `add_expense` with the validated amount, the category, and the date.
3. Confirm success from the response by checking that the created record's fields match what was requested.
4. Report the newly created expense back to the user.

## Constraints

- The amount must be positive and carry at most two decimal places; `validate_amount` is the pre-call guardrail and must run before any call.
- Never write to the database directly; the recorded expense goes through the single add operation only.
- If validation fails, do not proceed; surface the validation error instead.

## Example

User: "Add lunch for 12.50 under Food today."

1. `validate_amount(12.50)` passes: positive, two decimal places.
2. Call `add_expense` with amount 12.50, category Food, and today's date.
3. Confirm success from the response, then tell the user the expense was recorded.

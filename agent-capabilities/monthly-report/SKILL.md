---
name: monthly-report
description: Produce a monthly spending report with totals, top categories, and budget warnings.
---

# monthly-report

## When to Use

Use this skill when the user asks how much they spent in a given month,
which categories dominated their spending, or asks for a monthly summary
report of their expenses.

## Steps

1. Call `monthly_summary` for the requested month to obtain the total spend and the per-category breakdown.
2. Call `list_expenses` for the same month only when the user asks for line-level detail or a category drill-down.
3. Rank the categories by amount and pick the top categories for the report.
4. Compare the total against the monthly budget threshold: raise a warning when usage passes 80% of the budget, and state plainly when the user has exceeded your budget (over_amount).
5. Fill the results into the Report Template below and present it to the user.

## Report Template

```
Monthly Report - <month>
Total spent: <total>
Top categories:
  1. <category> - <amount>
  2. <category> - <amount>
Budget status: <within budget | over 80% | exceeded your budget by <amount>>
```

## Warnings

- If spending is above 80% of the budget, include a "watch your spending" warning.
- If the total exceeds the budget, say the user has exceeded your budget and give the over_amount by which it was exceeded.
- If there are no expenses for the month, say so instead of inventing numbers.

## Notes

- This skill is read-only: it never creates, updates, or deletes records.
- All figures come from the summary and expense listings; never estimate or round away precision.

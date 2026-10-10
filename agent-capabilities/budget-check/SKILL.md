---
name: budget-check
description: Report budget usage and warn when spending passes 80 percent or is exceeded.
---

# budget-check

## When to Use

Use this skill when the user asks how their budget is doing, how much
budget is left, or whether they are close to or over their budget.

## Steps

1. Call `get_budget_status` to fetch the current period's budget, spent amount, and remaining amount.
2. Compute the usage percentage as spent divided by the budget.
3. Warn when usage exceeds 80% of the budget that the user is approaching their limit.
4. When the response shows the budget is exceeded (an over_amount greater than zero), state plainly that the user has exceeded your budget and by how much.
5. Fill the values into the Output Template below and present it.

## Output Template

```
Budget Check - <period>
Budget: <budget>
Spent: <spent> (<percentage>%)
Remaining: <remaining>
Status: <ok | over 80% warning | exceeded your budget by <over_amount>>
```

## Notes

- This skill is read-only: it only reports and warns, it never changes data.

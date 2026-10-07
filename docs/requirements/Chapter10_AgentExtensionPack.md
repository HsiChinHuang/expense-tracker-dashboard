# Chapter 10: Agent Extension Pack

## 10.1 Overview

The Agent Extension Pack is the set of reusable capabilities that extend
the base coding agent beyond its default behavior. It is required for
Criterion 12 and is the main differentiator between this project and a
plain CRUD application.

The pack has five components:

| Component | Directory | Purpose |
|---|---|---|
| Skills | `agent-capabilities/` | Repeatable procedures the agent can discover |
| Hooks | `agent-hooks/` | Guardrails that validate before actions |
| MCP Server | `mcp-server/` | Tools that expose backend operations |
| Subagents | `custom-agent/` | Specialized agents with separate contexts |
| Documentation | `docs/agent-extension-pack.md`, `docs/permissions.md` | How to use the pack |

### 10.1.1 Criterion 12 Requirements

Criterion 12 states that a full-credit extension pack must include:

- Project instructions
- A reusable workflow
- A subagent or specialist
- An MCP tool or server
- A hook or guardrail
- Permission notes

The mapping:

| Requirement | Artifact |
|---|---|
| Project instructions | AGENTS.md (Chapter 9) |
| Reusable workflow | `docs/process.md` (Chapter 9) |
| Subagent / specialist | `custom-agent/finance-analyst.md`, `custom-agent/qa-reviewer.md` |
| MCP tool / server | `mcp-server/` with 4 tools |
| Hook / guardrail | `agent-hooks/validate-amount.py`, `agent-hooks/validate-ownership.py` |
| Permission notes | `docs/permissions.md` |

### 10.1.2 Directory Layout

```
agent-capabilities/
├── monthly-report/
│   └── SKILL.md
├── add-expense/
│   └── SKILL.md
└── budget-check/
    └── SKILL.md

agent-hooks/
├── validate-amount.py
├── validate-ownership.py
├── __init__.py
└── README.md

mcp-server/
├── server.py
├── auth.py
├── config.py
├── tools/
│   ├── __init__.py
│   ├── add_expense.py
│   ├── get_budget_status.py
│   ├── monthly_summary.py
│   └── list_expenses.py
├── pyproject.toml
└── README.md

custom-agent/
├── finance-analyst.md
└── qa-reviewer.md

docs/
├── agent-extension-pack.md
└── permissions.md

.agents/
├── skills/
│   ├── monthly-report -> ../../agent-capabilities/monthly-report
│   ├── add-expense -> ../../agent-capabilities/add-expense
│   └── budget-check -> ../../agent-capabilities/budget-check
└── agents/
    ├── finance-analyst.md -> ../../custom-agent/finance-analyst.md
    └── qa-reviewer.md -> ../../custom-agent/qa-reviewer.md
```

### 10.1.3 Why Symlinks

Agent tools expect skills in `.agents/skills/` and subagents in
`.agents/agents/`. The canonical files live in clearly named directories
at the repository root. Symlinks connect them.

| Benefit | Explanation |
|---|---|
| Single source of truth | Content lives in one place |
| Discoverable | Agent tools find them in the expected location |
| Reviewer-friendly | Top-level directories are self-documenting |
| No duplication | No risk of drift between copies |

## 10.2 Skills (agent-capabilities/)

### 10.2.1 Skill Format

Each skill is a markdown file with YAML frontmatter. The frontmatter
contains a `name` and `description` that the agent uses for discovery.

```markdown
---
name: <skill-name>
description: <one-line description of when to use this skill>
---

# <Skill Title>

## Steps

1. ...
2. ...
```

### 10.2.2 Skill: monthly-report

**File**: `agent-capabilities/monthly-report/SKILL.md`

```markdown
---
name: monthly-report
description: Generate a monthly expense report with budget analysis
---

# Monthly Report

## When to Use

Use this skill when the user asks for a monthly summary, report, or
review of their spending.

## Steps

1. Determine the target month.
   - If the user specifies a month, use it.
   - Otherwise, use the current month.
2. Call `get_budget_status` for the target month.
3. Call `monthly_summary` for the category breakdown.
4. Format the report using the template below.
5. Do not modify any data.
6. Do not include raw transaction IDs.

## Report Template

# Expense Report: {year_month}

## Summary

- Total spent: ${total}
- Budget: ${budget}
- Remaining: ${remaining}
- Usage: {percentage}%

## Top Categories

1. {category} - ${amount} ({percentage}%)
2. {category} - ${amount} ({percentage}%)
3. {category} - ${amount} ({percentage}%)

## Warnings

- If percentage > 90%: "You have used more than 90% of your budget."
- If is_over_budget: "You have exceeded your budget by ${over_amount}."

## Notes

- Amounts are in USD.
- The report reflects only recorded expenses.
```

### 10.2.3 Skill: add-expense

**File**: `agent-capabilities/add-expense/SKILL.md`

```markdown
---
name: add-expense
description: Add a new expense with validation
---

# Add Expense

## When to Use

Use this skill when the user wants to record a new expense.

## Steps

1. Confirm with the user:
   - Amount (required)
   - Category (required, must be from their categories)
   - Date (required, default to today)
   - Note (optional)
2. Validate the amount using the `validate_amount` hook.
   - Must be positive.
   - Must have at most 2 decimal places.
   - Must not exceed 1,000,000.
3. Call the `add_expense` MCP tool.
4. Confirm success with the created expense details.
5. If validation fails, explain the error and ask again.

## Constraints

- Never skip amount validation.
- Never create an expense for another user.
- Never use float for the amount.

## Example

User: "I spent 45 dollars on lunch today."

Agent:
1. Confirms: "Adding $45.00 to Food & Dining for today. Any note?"
2. User: "Lunch with team"
3. Validates amount: 45.00 is positive, 2 decimals, under limit.
4. Calls `add_expense` with amount="45.00", category="Food & Dining",
   date=<today>, note="Lunch with team".
5. Reports: "Added $45.00 to Food & Dining on <date>."
```

### 10.2.4 Skill: budget-check

**File**: `agent-capabilities/budget-check/SKILL.md`

```markdown
---
name: budget-check
description: Check current budget status and warn if overspending
---

# Budget Check

## When to Use

Use this skill when the user asks about their budget, remaining
balance, or spending pace.

## Steps

1. Determine the target month.
   - Default to the current month.
2. Call `get_budget_status`.
3. Report:
   - Budget amount
   - Spent so far
   - Remaining
   - Percentage used
4. If percentage > 80%, list the top 3 categories from
   `monthly_summary`.
5. If over budget, suggest reviewing recent expenses.
6. Do not modify data.

## Output Template

# Budget Status: {year_month}

- Budget: ${budget}
- Spent: ${spent}
- Remaining: ${remaining}
- Used: {percentage}%

{if percentage > 80}
You are approaching your budget limit. Top categories:

1. {category} - ${amount}
2. {category} - ${amount}
3. {category} - ${amount}
{endif}

{if is_over_budget}
You have exceeded your budget by ${over_amount}. Consider
reviewing your recent expenses.
{endif}
```

### 10.2.5 Skill Discovery and Invocation

| Mechanism | How |
|---|---|
| Auto-discovery | Agent loads skill list at session start |
| Natural language | "Generate a monthly report" triggers monthly-report |
| Explicit command | Agent may be told "use the budget-check skill" |

### 10.2.6 Skill Design Principles

| Principle | Rationale |
|---|---|
| One procedure per skill | Easier to discover and reuse |
| Clear "When to Use" | Helps the agent decide |
| Numbered steps | Deterministic execution |
| Explicit constraints | Prevents common mistakes |
| No side effects in read-only skills | Safety |
| Templates for output | Consistent results |

## 10.3 Hooks (agent-hooks/)

### 10.3.1 Hook Purpose

Hooks are guardrails that run before an action. They validate inputs
and raise errors when rules are violated. They are pure functions with
no side effects.

### 10.3.2 Hook: validate-amount

**File**: `agent-hooks/validate-amount.py`

```python
"""
Hook: validate_amount

Validates an amount string before it is used to create or update
an expense.

Rules:
- Must be a valid number
- Must be positive
- Must not exceed MAX_AMOUNT
- Must have at most 2 decimal places

Raises ValueError with a clear message on failure.
Returns the parsed Decimal on success.
"""

from decimal import Decimal, InvalidOperation

MAX_AMOUNT = Decimal("1000000.00")


def validate_amount(amount: str) -> Decimal:
    if amount is None or amount == "":
        raise ValueError("Amount is required")

    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError("Amount must be a valid number")

    if value <= 0:
        raise ValueError("Amount must be positive")

    if value > MAX_AMOUNT:
        raise ValueError(f"Amount exceeds maximum of {MAX_AMOUNT}")

    if value.as_tuple().exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places")

    return value
```

### 10.3.3 Hook: validate-ownership

**File**: `agent-hooks/validate-ownership.py`

```python
"""
Hook: validate_ownership

Verifies that the current user owns a resource before the agent
reads, updates, or deletes it.

Raises PermissionError if the resource belongs to another user.
"""


def validate_ownership(current_user_id: str, resource_user_id: str) -> None:
    if current_user_id is None or resource_user_id is None:
        raise PermissionError("Missing user identity")

    if current_user_id != resource_user_id:
        raise PermissionError(
            "Access denied: resource belongs to another user"
        )
```

### 10.3.4 Hook Triggers

| Hook | Triggered When | Called From |
|---|---|---|
| validate_amount | Before creating an expense via MCP | `mcp-server/tools/add_expense.py` |
| validate_amount | Before updating an expense via MCP | `mcp-server/tools/` |
| validate_amount | Before accepting an expense via API | Backend Pydantic schema |
| validate_ownership | Before reading a resource via MCP | MCP tool wrapper |
| validate_ownership | Before updating a resource via MCP | MCP tool wrapper |
| validate_ownership | Before deleting a resource via MCP | MCP tool wrapper |
| validate_ownership | Before any query on user data | Backend service layer |

### 10.3.5 Hook README

**File**: `agent-hooks/README.md`

```markdown
# Agent Hooks

Guardrails that run before agent actions.

## validate_amount

- Trigger: before creating or updating an expense
- Checks:
  - Amount is present
  - Amount is a valid number
  - Amount is positive
  - Amount does not exceed 1,000,000
  - Amount has at most 2 decimal places
- On failure: raises ValueError
- Agent behavior: report the error to the user and ask again

## validate_ownership

- Trigger: before reading, updating, or deleting a resource
- Checks: resource.user_id == current_user.id
- On failure: raises PermissionError
- Agent behavior: report the error and do not proceed

## Design Notes

- Hooks are pure functions with no side effects.
- Hooks do not access the database. They only validate inputs.
- Hooks are also enforced in the backend for defense in depth.
- Hooks raise exceptions; they do not return booleans.
```

### 10.3.6 Defense in Depth

Hooks are one layer. The same rules are enforced at multiple layers:

| Rule | Hook | MCP | Backend Schema | Backend Service | Database |
|---|---|---|---|---|---|
| Amount positive | Yes | Yes | Yes | - | Yes |
| Amount 2 decimals | Yes | - | Yes | - | - |
| Amount max | Yes | - | Yes | - | - |
| User ownership | Yes | Yes | - | Yes | FK |
| Category ownership | - | - | - | Yes | FK |

## 10.4 MCP Server (mcp-server/)

### 10.4.1 Purpose

The MCP server exposes backend operations as tools the agent can call.
It authenticates with JWT and calls the backend API. It never accesses
the database directly.

### 10.4.2 Architecture

```
┌──────────────┐
│  pi-agent    │
└──────┬───────┘
       │ stdio
       ▼
┌──────────────┐
│  MCP Server  │
│              │
│  - auth.py   │
│  - tools/    │
└──────┬───────┘
       │ HTTP + JWT
       ▼
┌──────────────┐
│  Backend API │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Database    │
└──────────────┘
```

### 10.4.3 Configuration

**File**: `mcp-server/config.py`

```python
import os


class MCPSettings:
    JWT_SECRET: str = os.environ["MCP_JWT_SECRET"]
    API_BASE_URL: str = os.environ.get(
        "MCP_API_BASE_URL", "http://localhost:8000/api/v1"
    )
    USER_TOKEN: str = os.environ.get("MCP_USER_TOKEN", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "expense-tracker"
    JWT_AUDIENCE: str = "expense-tracker-api"


settings = MCPSettings()
```

### 10.4.4 Authentication

**File**: `mcp-server/auth.py`

```python
import jwt
from config import settings


def verify_jwt(token: str) -> str:
    """
    Verify a JWT and return the user_id (sub claim).
    Raises ValueError on any failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Missing subject")

    return user_id


def get_user_token() -> str:
    if not settings.USER_TOKEN:
        raise RuntimeError("MCP_USER_TOKEN is not set")
    return settings.USER_TOKEN
```

### 10.4.5 Tool: add_expense

**File**: `mcp-server/tools/add_expense.py`

```python
import httpx
from config import settings
from agent_hooks.validate_amount import validate_amount


async def add_expense(user_id: str, token: str, args: dict) -> dict:
    amount = validate_amount(args["amount"])

    payload = {
        "amount": str(amount),
        "category_id": args["category_id"],
        "date": args["date"],
        "note": args.get("note"),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.API_BASE_URL}/expenses",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
```

### 10.4.6 Tool: get_budget_status

**File**: `mcp-server/tools/get_budget_status.py`

```python
import httpx
from config import settings


async def get_budget_status(user_id: str, token: str, args: dict) -> dict:
    year_month = args["year_month"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_BASE_URL}/dashboard/summary",
            params={"year_month": year_month},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "year_month": data["year_month"],
        "budget": data["budget"],
        "spent": data["total_spent"],
        "remaining": data["remaining"],
        "percentage": data["percentage"],
        "is_over_budget": data["is_over_budget"],
        "transaction_count": data["transaction_count"],
    }
```

### 10.4.7 Tool: monthly_summary

**File**: `mcp-server/tools/monthly_summary.py`

```python
import httpx
from config import settings


async def monthly_summary(user_id: str, token: str, args: dict) -> dict:
    year_month = args["year_month"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_BASE_URL}/dashboard/by-category",
            params={"year_month": year_month},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
```

### 10.4.8 Tool: list_expenses

**File**: `mcp-server/tools/list_expenses.py`

```python
import httpx
from config import settings


async def list_expenses(user_id: str, token: str, args: dict) -> dict:
    params = {}
    if "year_month" in args:
        params["year_month"] = args["year_month"]
    if "category_id" in args:
        params["category_id"] = args["category_id"]
    if "limit" in args:
        params["page_size"] = args["limit"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.API_BASE_URL}/expenses",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
```

### 10.4.9 Tool Schemas

**add_expense**:

```json
{
  "name": "add_expense",
  "description": "Create a new expense for the authenticated user",
  "inputSchema": {
    "type": "object",
    "required": ["amount", "category_id", "date"],
    "properties": {
      "amount": {
        "type": "string",
        "pattern": "^\\d+(\\.\\d{1,2})?$",
        "description": "Expense amount in USD as a string"
      },
      "category_id": {
        "type": "string",
        "format": "uuid"
      },
      "date": {
        "type": "string",
        "format": "date"
      },
      "note": {
        "type": "string",
        "maxLength": 500
      }
    }
  }
}
```

**get_budget_status**:

```json
{
  "name": "get_budget_status",
  "description": "Get budget status for a given month",
  "inputSchema": {
    "type": "object",
    "required": ["year_month"],
    "properties": {
      "year_month": {
        "type": "string",
        "pattern": "^\\d{4}-\\d{2}$"
      }
    }
  }
}
```

**monthly_summary**:

```json
{
  "name": "monthly_summary",
  "description": "Get category breakdown for a month",
  "inputSchema": {
    "type": "object",
    "required": ["year_month"],
    "properties": {
      "year_month": {
        "type": "string",
        "pattern": "^\\d{4}-\\d{2}$"
      }
    }
  }
}
```

**list_expenses**:

```json
{
  "name": "list_expenses",
  "description": "List expenses with optional filters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "year_month": {
        "type": "string",
        "pattern": "^\\d{4}-\\d{2}$"
      },
      "category_id": {
        "type": "string",
        "format": "uuid"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 50,
        "default": 20
      }
    }
  }
}
```

### 10.4.10 MCP Server README

**File**: `mcp-server/README.md`

```markdown
# MCP Server

Exposes backend operations as MCP tools for the coding agent.

## Tools

| Tool | Input | Output |
|---|---|---|
| add_expense | amount, category_id, date, note | Expense object |
| get_budget_status | year_month | Budget summary |
| monthly_summary | year_month | Category breakdown |
| list_expenses | year_month, category_id, limit | Paginated list |

## Authentication

The server uses JWT. The token is provided via `MCP_USER_TOKEN`.

Required environment variables:

- `MCP_JWT_SECRET` — same secret as the backend
- `MCP_API_BASE_URL` — backend API base URL
- `MCP_USER_TOKEN` — user access token

## Running

```bash
export MCP_JWT_SECRET="same-as-backend"
export MCP_API_BASE_URL="http://localhost:8000/api/v1"
export MCP_USER_TOKEN="<jwt>"
python server.py
```

## Design

- The server calls the backend API. It does not access the database.
- All authorization happens in the backend.
- Hooks validate inputs before API calls.
- Errors are raised as exceptions with clear messages.
```

## 10.5 Subagents (custom-agent/)

### 10.5.1 Purpose

Subagents run in separate contexts. Each has a clear role and does not
see the orchestrator's history. This enables independent verification
and focused analysis.

### 10.5.2 Subagent: finance-analyst

**File**: `custom-agent/finance-analyst.md`

```markdown
---
name: finance-analyst
description: Analyze spending patterns and suggest budget adjustments
---

# Finance Analyst

You analyze a user's spending patterns. You do not modify data.

## Input

- Target month (default: current month)

## Steps

1. Fetch the monthly summary using `get_budget_status`.
2. Fetch the category breakdown using `monthly_summary`.
3. Identify:
   - Categories where spending exceeds 80% of the monthly budget
   - Categories with month-over-month change greater than 20%
   - Transactions with amount greater than 2x the category average
4. Compare the current month to the previous 3 months.
5. Produce the output using the template below.

## Output Template

# Spending Analysis: {year_month}

## Overview

- Total: ${total}
- vs last month: {change}%
- vs 3-month average: {change}%

## Categories of Concern

- {category}: ${amount} ({percentage}% of budget)

## Unusual Transactions

- {date}: ${amount} in {category}

## Suggestions

1. ...
2. ...

## Limitations

- Analysis is based only on recorded expenses.
- Does not include income or external accounts.

## Rules

- Read-only. Never modify data.
- Never expose raw user IDs.
- Never include transaction IDs in the output.
- If data is insufficient, say so instead of guessing.
```

### 10.5.3 Subagent: qa-reviewer

**File**: `custom-agent/qa-reviewer.md`

```markdown
---
name: qa-reviewer
description: Verify expense tracker features against acceptance criteria
---

# QA Reviewer

You verify that finished work meets the issue's acceptance criteria.

## Steps

1. Read the issue and its acceptance criteria.
2. For each criterion:
   - Check the implementation against the running application.
   - Run the relevant tests.
   - Record PASS or FAIL with evidence.
3. Run the full test suite and report the result.
4. Post the verdict as a comment on the issue.

## Output Format

## QA: {PASS|FAIL}

- [x] {criterion 1} - PASS
- [ ] {criterion 2} - FAIL
      Steps: {what you did}
      Expected: {what should happen}
      Actual: {what happened}

Tests: `{command}`, {passed} passed, {failed} failed

## Rules

- Do not fix anything.
- Do not modify code.
- Ignore what the implementation claims it does.
- Only the acceptance criteria and running code count.
- If any criterion fails, overall verdict is FAIL.
- Always include the test command and its result.
```

### 10.5.4 Subagent Launch Commands

| Command | Effect |
|---|---|
| `Launch a subagent to implement #12` | Orchestrator spawns SWE subagent |
| `Launch software engineer for #12` | Uses named subagent definition |
| `Launch QA for #12` | Spawns QA subagent |
| `Launch finance analyst for 2026-10` | Spawns analyst subagent |

### 10.5.5 Subagent Isolation

| Aspect | Behavior |
|---|---|
| Context | Fresh, plus AGENTS.md |
| History | Does not see orchestrator history |
| Output | Posted back to orchestrator or issue |
| Tools | Same as base agent, restricted by role rules |
| Permissions | Enforced by MCP and backend |

## 10.6 Documentation (docs/agent-extension-pack.md)

### 10.6.1 Purpose

This document explains what the extension pack contains and how to use
it. A reviewer should be able to read this one file and understand the
whole pack.

### 10.6.2 Document Content

```markdown
# Agent Extension Pack

This document describes the reusable capabilities that extend the
base coding agent for this project.

## Contents

| Component | Directory | Purpose |
|---|---|---|
| Skills | `agent-capabilities/` | Repeatable procedures |
| Hooks | `agent-hooks/` | Input guardrails |
| MCP Server | `mcp-server/` | Backend tools |
| Subagents | `custom-agent/` | Specialized agents |
| Permissions | `docs/permissions.md` | Access matrix |

## Skills

| Skill | Purpose |
|---|---|
| monthly-report | Generate a monthly expense report |
| add-expense | Add an expense with validation |
| budget-check | Check budget status and warn if overspending |

### Using a Skill

The agent discovers skills automatically. You can also invoke one
explicitly:

```
Use the monthly-report skill for 2026-10
```

## Hooks

| Hook | Purpose |
|---|---|
| validate_amount | Reject invalid amounts before creating an expense |
| validate_ownership | Reject access to another user's resources |

### Hook Behavior

Hooks raise exceptions. The agent must catch them and report the error
to the user. Hooks are also enforced in the backend.

## MCP Server

| Tool | Purpose |
|---|---|
| add_expense | Create an expense |
| get_budget_status | Get budget status |
| monthly_summary | Get category breakdown |
| list_expenses | List expenses |

### Running the MCP Server

The MCP server is started by the agent as a subprocess. Configuration
is via environment variables:

- `MCP_JWT_SECRET`
- `MCP_API_BASE_URL`
- `MCP_USER_TOKEN`

## Subagents

| Subagent | Purpose |
|---|---|
| finance-analyst | Analyze spending patterns |
| qa-reviewer | Verify work against acceptance criteria |

### Launching a Subagent

```
Launch QA for issue #12
```

## Permissions

See `docs/permissions.md` for the full access matrix.

## Design Principles

1. Single source of truth: content lives in one place, symlinks make it discoverable.
2. Defense in depth: hooks, MCP, backend, and database all enforce rules.
3. Separation of concerns: skills describe procedures, hooks validate, MCP executes, subagents specialize.
4. Read-only by default: analytical agents never modify data.
5. JWT everywhere: the same authentication mechanism is used across frontend, backend, and MCP.
```

## 10.7 Permissions (docs/permissions.md)

### 10.7.1 Document Content

```markdown
# Permissions

## User Roles

| Role | Description |
|---|---|
| User | Regular authenticated user |
| System | Backend service |
| Agent | Coding agent acting on behalf of a user |

## Resource Permissions

| Resource | User | System | Agent |
|---|---|---|---|
| Own expenses | Read/Write | Read/Write | Read/Write via MCP |
| Other users' expenses | None | Read/Write | None |
| Own budgets | Read/Write | Read/Write | Read/Write via MCP |
| Other users' budgets | None | Read/Write | None |
| System categories | Read | Read/Write | Read |
| Own categories | Read/Write | Read/Write | Read via MCP |
| Audit logs | None | Read/Write | None |

## Agent Permissions by Role

| Agent | Read Expenses | Write Expenses | Read Budgets | Write Budgets | Read Audit |
|---|---|---|---|---|---|
| finance-analyst | Own | None | Own | None | None |
| qa-reviewer | Test data | Test data | Test data | Test data | None |
| MCP add_expense | None | Own | None | None | None |
| MCP get_budget_status | Own | None | Own | None | None |
| MCP monthly_summary | Own | None | Own | None | None |
| MCP list_expenses | Own | None | None | None | None |

## Skill Permissions

| Skill | Reads | Writes |
|---|---|---|
| monthly-report | Budget, summary | None |
| add-expense | Categories | Expenses |
| budget-check | Budget, summary | None |

## Subagent Permissions

| Subagent | Reads | Writes | Scope |
|---|---|---|---|
| finance-analyst | Budget, summary, expenses | None | Current user |
| qa-reviewer | Test data | Test data | Test environment only |

## Enforcement Layers

| Layer | What It Enforces |
|---|---|
| Hook | Input validity, ownership before call |
| MCP server | JWT verification, user_id extraction |
| Backend dependency | Current user from token |
| Backend service | Query filter by user_id |
| Backend test | Cross-user access returns 404 |
| Database | Foreign keys, constraints |

## Forbidden Actions

Agents must never:

- Read or write another user's data
- Modify system categories
- Access audit logs
- Delete user accounts
- Change permissions
- Bypass the backend API
- Access the database directly
- Include secrets or tokens in output

## Escalation

If an agent encounters a permission error:

1. Stop the current action.
2. Report the error to the user or orchestrator.
3. Do not retry with different credentials.
4. Do not attempt to bypass the restriction.
```

## 10.8 How the Pack Is Verified

### 10.8.1 Verification Checklist

| Item | How to Verify |
|---|---|
| Skills exist and are valid | Check `agent-capabilities/*/SKILL.md` frontmatter |
| Skills are discoverable | Check `.agents/skills/` symlinks |
| Hooks are callable | Import and call in a Python shell |
| MCP server starts | Run with required env vars |
| MCP tools work | Call each tool against a running backend |
| Subagents are defined | Check `custom-agent/*.md` frontmatter |
| Subagents are discoverable | Check `.agents/agents/` symlinks |
| Permissions documented | Read `docs/permissions.md` |
| Extension pack documented | Read `docs/agent-extension-pack.md` |

### 10.8.2 Manual Test Commands

```bash
# Skills
ls agent-capabilities/
cat agent-capabilities/monthly-report/SKILL.md

# Hooks
python -c "from agent_hooks.validate_amount import validate_amount; print(validate_amount('125.50'))"
python -c "from agent_hooks.validate_amount import validate_amount; validate_amount('-5')"  # should raise

# MCP server
export MCP_JWT_SECRET="test"
export MCP_API_BASE_URL="http://localhost:8000/api/v1"
export MCP_USER_TOKEN="<token>"
python mcp-server/server.py

# Subagents
ls custom-agent/
cat custom-agent/qa-reviewer.md

# Symlinks
ls -la .agents/skills/
ls -la .agents/agents/

# Documentation
cat docs/agent-extension-pack.md
cat docs/permissions.md
```

### 10.8.3 Automated Verification

A test in `backend/tests/integration/test_agent_hooks.py` imports the
hooks and verifies their behavior:

```python
import pytest
from agent_hooks.validate_amount import validate_amount
from agent_hooks.validate_ownership import validate_ownership


def test_validate_amount_accepts_valid():
    assert validate_amount("125.50") == Decimal("125.50")


def test_validate_amount_rejects_negative():
    with pytest.raises(ValueError, match="positive"):
        validate_amount("-5")


def test_validate_amount_rejects_three_decimals():
    with pytest.raises(ValueError, match="2 decimal"):
        validate_amount("125.505")


def test_validate_ownership_accepts_same_user():
    validate_ownership("user-a", "user-a")


def test_validate_ownership_rejects_different_user():
    with pytest.raises(PermissionError):
        validate_ownership("user-a", "user-b")
```

## 10.9 Extension Pack Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Skills location | `agent-capabilities/` | Descriptive, top-level |
| Skills discovery | `.agents/skills/` symlinks | Agent tool convention |
| Hook language | Python | Same as backend, importable in tests |
| Hook style | Raise exceptions | Clear failure, cannot be ignored |
| MCP transport | stdio subprocess | Simple, started by agent |
| MCP auth | JWT | Same as backend, no new mechanism |
| MCP data access | Via backend API | Single permission layer |
| Subagent location | `custom-agent/` | Descriptive, top-level |
| Subagent discovery | `.agents/agents/` symlinks | Agent tool convention |
| Read-only agents | finance-analyst | Safety, analysis only |
| Verification agent | qa-reviewer | Independent, does not fix |
| Documentation | Two files | Pack overview + permissions |
| Verification | Manual + automated | Both human and CI can check |
```

---

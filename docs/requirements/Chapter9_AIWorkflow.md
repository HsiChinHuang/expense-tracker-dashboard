# Chapter 9: AI Workflow

## 9.1 Overview

This project follows an AI-native development workflow based on the
AI Dev Tools Zoomcamp course. The workflow has four layers:

| Layer | Purpose | Artifacts |
|---|---|---|
| Context | What the agent knows at session start | AGENTS.md, CLAUDE.md, docs/ |
| Roles | Specialized agents with clear responsibilities | docs/team/*.md |
| Orchestration | How work moves between roles | docs/process.md |
| Extension | Reusable capabilities beyond the base agent | agent-capabilities/, agent-hooks/, mcp-server/, custom-agent/ |

The workflow is tool-agnostic in structure but implemented with
pi-agent + qwen3.8-27b in this project.

## 9.2 Tool Selection

### 9.2.1 Primary Tools

| Tool | Role | Notes |
|---|---|---|
| pi-agent | Primary coding agent | Reads AGENTS.md, discovers skills, launches subagents |
| qwen3.8-27b | Local LLM | Runs locally, no cloud dependency |
| Plugins | Extend pi-agent capabilities | Added when a capability is missing |

### 9.2.2 Confirmed Capabilities

pi-agent supports the following, with plugins available for gaps:

| Capability | Status | Notes |
|---|---|---|
| Read AGENTS.md | Supported | At every session start |
| Discover skills | Supported | From `.agents/skills/` |
| Launch subagents | Supported | Separate context per subagent |
| Tool use / function calling | Supported | Used for MCP server tools |
| File operations | Supported | Read, write, edit |
| Command execution | Supported | Shell commands |

### 9.2.3 Why Local Model

| Reason | Explanation |
|---|---|
| Data privacy | Code and prompts never leave the machine |
| No API cost | No per-token billing |
| Offline capability | Works without internet |
| Reproducibility | Same model version across sessions |
| Learning | Full visibility into agent behavior |

### 9.2.4 Local Model Limitations

| Limitation | Mitigation |
|---|---|
| Smaller context window | Keep AGENTS.md short; load docs on demand |
| Slower inference | Smaller issues; accept longer sessions |
| Less capable at complex tasks | More grooming; smaller task units |
| Function calling may be less reliable | Simpler MCP tool schemas |

## 9.3 Context Engineering

### 9.3.1 AGENTS.md

AGENTS.md is read at the start of every session. It must be short and
contain only essential information.

```markdown
# AGENTS.md

## Commands

- `make dev` — start full development environment
- `make test` — run all tests
- `make test-backend` — backend tests only
- `make test-frontend` — frontend tests only
- `make e2e` — end-to-end tests (requires docker compose up)
- `make lint` — lint backend and frontend
- `make migrate` — run database migrations
- `make security` — run all security scans

## Rules

- Backend uses uv for dependency management. Do not edit pyproject.toml manually.
- Money must use Decimal, never float.
- All database queries must filter by user_id.
- Run `make test` and `make lint` before committing.
- Never commit .env or any secret.
- Follow openapi.yaml exactly when implementing endpoints.

## Documents

- `docs/process.md` — workflow and roles
- `docs/architecture.md` — system architecture
- `docs/design-system.md` — UI conventions
- `docs/testing-guidelines.md` — testing rules
- `docs/api.md` — API usage notes
- Before writing tests, read `docs/testing-guidelines.md`
- For UI work, read `docs/design-system.md`
```

### 9.3.2 CLAUDE.md

A single line that points to AGENTS.md:

```
@AGENTS.md
```

This makes the context tool-agnostic. Any agent that reads CLAUDE.md
will follow the same instructions.

### 9.3.3 Supporting Documents

| Document | Read When |
|---|---|
| `docs/process.md` | Every task (defines workflow) |
| `docs/architecture.md` | Understanding system structure |
| `docs/design-system.md` | Any UI task |
| `docs/testing-guidelines.md` | Before writing tests |
| `docs/api.md` | Any API-related task |
| `openapi.yaml` | Backend implementation |
| `docs/team/pm.md` | When acting as PM |
| `docs/team/software-engineer.md` | When acting as SWE |
| `docs/team/qa-engineer.md` | When acting as QA |

### 9.3.4 Context Loading Strategy

AGENTS.md links to other documents instead of including them inline.
The agent loads a document only when the current task requires it.

| Task Type | Documents Loaded |
|---|---|
| Backend endpoint | AGENTS.md, process.md, api.md, openapi.yaml |
| Frontend UI | AGENTS.md, process.md, design-system.md |
| Testing | AGENTS.md, process.md, testing-guidelines.md |
| PM grooming | AGENTS.md, process.md, team/pm.md |
| QA verification | AGENTS.md, process.md, team/qa-engineer.md |

This keeps the initial context small and loads details on demand.

### 9.3.5 Context Files as Living Documents

When an agent makes a mistake, the correction is written into the
relevant document so it does not repeat.

Prompt used:

```
Based on the corrections I made, find the relevant documents and update them.
Commit the current work before changing the documents.
```

This turns every correction into a permanent improvement.

## 9.4 Role Definitions

### 9.4.1 PM Agent

**File**: `docs/team/pm.md`

```markdown
You're a Product Manager.

You groom a task before anyone implements it.

- Read the issue as written
- Rewrite it using the template in `docs/task-template.md`
- Make the acceptance criteria checkable - someone should be able to
  point at the screen and say yes or no
- Think about the edge cases the person who filed it did not consider
- Do not write any code

Definition of done:

- The issue has all four sections filled in
- Every acceptance criterion can be checked by looking at the result
- Everything moved out of scope links to a follow-up issue
- An engineer who has never spoken to you could implement it from the
  issue and the documents it links

If something does not belong in this task, do not silently drop it.
File a follow-up issue and list it under out of scope with a link to
that issue, so it is clear what was moved and where it went.
```

### 9.4.2 SWE Agent

**File**: `docs/team/software-engineer.md`

```markdown
You're a Software Engineer.

You implement one groomed task at a time.

- Read the issue and implement what it describes
- Implement against the acceptance criteria, do not change them
- Stay inside the files and constraints the issue names
- Write tests for what you built
- Do not close the issue
- Commit regularly

Definition of done:

- Every acceptance criterion in the issue is implemented
- Tests are written for the new behaviour, and the whole suite passes
- The work is committed
- The issue is still open, with a comment saying what you did

If an acceptance criterion is wrong, impossible, or contradicts another
one, create a comment on the issue about it.
```

### 9.4.3 QA Agent

**File**: `docs/team/qa-engineer.md`

```markdown
You're a QA Engineer.

You check finished work against the issue that specified it.

- Read the acceptance criteria from the issue
- Check each one against what the code actually does
- Run the tests, and say which ones you ran
- Look for the cases the criteria describe but the tests do not cover
- Do not fix anything you find. Report it by creating a comment

Your output is a verdict: PASS or FAIL. It is FAIL if a single
acceptance criterion fails. Post it as a comment on the issue.

Definition of done:

- The comment starts with PASS or FAIL
- Every acceptance criterion has a verdict against it
- Every FAIL says what you did and what happened
- The test command and its result are included
- Nothing in the code was changed

Ignore what the implementation says it does. Only the acceptance
criteria and the running code count.
```

### 9.4.4 Role Summary

| Role | Input | Output | Writes Code |
|---|---|---|---|
| PM | Raw issue | Groomed issue | No |
| SWE | Groomed issue | Code + tests + commit | Yes |
| QA | Groomed issue + code | PASS/FAIL comment | No |

## 9.5 Orchestration

### 9.5.1 Orchestrator Definition

**File**: `docs/process.md`

```markdown
# Process

## Roles

- PM — grooms a task before anyone implements it, follows `docs/team/pm.md`
- Engineer — implements one groomed task, follows `docs/team/software-engineer.md`
- QA — checks the result against acceptance criteria, follows `docs/team/qa-engineer.md`

## Orchestrator

The main session is the orchestrator. It launches the PM, the engineer
and QA as subagents. It does not groom, implement or test itself.

## Lifecycle

1. Pick the next open issue from the backlog
2. PM grooms it
3. Engineer implements it
4. QA verifies it
5. On FAIL, back to step 3 with the QA comment as input
6. On PASS, close the issue
7. Repeat until the backlog is empty

## Rules

- Do not skip step 2
- The engineer does not close the issue
- QA does not fix the code, only outputs PASS or FAIL
- The orchestrator closes the issue only after QA outputs PASS
- Tasks are GitHub issues, one at a time
- Commit regularly after each meaningful change
- Read acceptance criteria before starting and before closing
```

### 9.5.2 Workflow Diagram

```
┌─────────────┐
│  Backlog    │
│ (GitHub     │
│  Issues)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Orchestrator│
│ (main       │
│  session)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     PM      │  grooms issue
│  (subagent) │
└──────┬──────┘
       │ groomed issue
       ▼
┌─────────────┐
│    SWE      │  implements
│  (subagent) │
└──────┬──────┘
       │ code + tests + commit
       ▼
┌─────────────┐
│     QA      │  verifies
│  (subagent) │
└──────┬──────┘
       │
       ├── PASS ──▶ Orchestrator closes issue
       │
       └── FAIL ──▶ Back to SWE with QA comment
```

### 9.5.3 Sequential Execution

MVP uses sequential execution. Each issue flows through
PM → SWE → QA before the next issue starts.

| Reason | Explanation |
|---|---|
| Simpler | No worktree management |
| Predictable | One issue at a time |
| Easier to review | Focused changes |
| Fewer conflicts | No parallel branches |

Parallel execution with git worktrees is a future improvement, not
part of the MVP.

### 9.5.4 Orchestrator Commands

| Command | Purpose |
|---|---|
| `Groom issue #12` | Run PM agent on one issue |
| `Implement issue #12` | Run SWE agent on one issue |
| `Test issue #12` | Run QA agent on one issue |
| `/goal work through the backlog` | Run full loop until backlog is empty |

### 9.5.5 Loop Engineering

The `/goal` command keeps the orchestrator running until a stop
condition is met. For this project, the stop condition is:

> All issues in the backlog are groomed, implemented, and verified.

A stop condition must be checkable. The orchestrator can evaluate
whether each issue has a PASS comment from QA.

### 9.5.6 Graph Engineering

The workflow is a graph with specialized agents as nodes:

```
PM ──▶ SWE ──▶ QA
       ▲        │
       │        │
       └────────┘
        on FAIL
```

The orchestrator enforces the graph. Each agent runs in its own
context, so the QA agent is not biased by the SWE agent's history.

## 9.6 GitHub Issues as Backlog

### 9.6.1 Issue Template

**File**: `docs/task-template.md`

```markdown
## Goal

One or two sentences on what should be true when this is done.

## Acceptance criteria

- [ ] A statement you can check by looking at the result
- [ ] One line per case, including the awkward ones

## Out of scope

- Something that does not belong in this task, moved to #TASK-NUMBER

## Constraints

- Files this should stay inside
- Libraries to use
- Guidelines to follow
```

### 9.6.2 Example Groomed Issue

**Before grooming**:

```markdown
## Goal
Implement expense CRUD API

## Description
Need endpoints to create, read, update, delete expenses.
```

**After grooming**:

```markdown
## Goal

Implement expense CRUD REST endpoints with user isolation, following openapi.yaml.

## Acceptance criteria

- [ ] POST /api/v1/expenses creates an expense for the authenticated user
- [ ] POST /api/v1/expenses returns 201 with the created expense
- [ ] POST /api/v1/expenses rejects amount <= 0 with 422
- [ ] POST /api/v1/expenses rejects amount with >2 decimals with 422
- [ ] POST /api/v1/expenses rejects category_id not owned by user with 404
- [ ] GET /api/v1/expenses returns only the authenticated user's expenses
- [ ] GET /api/v1/expenses supports year_month, category_id, page, page_size filters
- [ ] GET /api/v1/expenses returns 422 for page < 1 or page_size > 100
- [ ] PUT /api/v1/expenses/{id} updates only the user's own expense
- [ ] PUT /api/v1/expenses/{id} returns 404 for another user's expense
- [ ] DELETE /api/v1/expenses/{id} deletes only the user's own expense
- [ ] DELETE /api/v1/expenses/{id} returns 404 for another user's expense
- [ ] Every create/update/delete writes an audit log entry
- [ ] All endpoints require valid JWT

## Out of scope

- Bulk delete (moved to #20)
- Expense search by note text (moved to #21)
- Recurring expenses (moved to #22)

## Constraints

- Stay inside `backend/app/routers/expenses.py`,
  `backend/app/services/expense_service.py`,
  `backend/app/schemas/expense.py`
- Use Decimal for amount, never float
- Follow openapi.yaml exactly
- Add tests in `backend/tests/integration/test_expenses_api.py`
- Read `docs/testing-guidelines.md` before writing tests
```

### 9.6.3 Issue Lifecycle

| State | Set By |
|---|---|
| Open, ungroomed | Human |
| Open, groomed | PM agent |
| Open, implemented | SWE agent (comments, does not close) |
| Open, QA FAIL | QA agent (comments) |
| Open, QA PASS | QA agent (comments) |
| Closed | Orchestrator |

## 9.7 Skills

### 9.7.1 Skill Structure

Skills are markdown files with YAML frontmatter, stored in
`agent-capabilities/<name>/SKILL.md`. A symlink makes them discoverable
from `.agents/skills/`.

```markdown
---
name: skill-name
description: One-line description of when to use this skill
---

# Skill Name

## Steps

1. Step one
2. Step two
```

### 9.7.2 Skill: monthly-report

**File**: `agent-capabilities/monthly-report/SKILL.md`

```markdown
---
name: monthly-report
description: Generate a monthly expense report with budget analysis
---

# Monthly Report

## Steps

1. Ask the user for the target month, or use the current month.
2. Call `get_budget_status` for that month.
3. Call `monthly_summary` for category breakdown.
4. Format a markdown report using the template below.
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
2. ...
3. ...

## Warnings

- [if percentage > 90%] You have used more than 90% of your budget.
- [if is_over_budget] You have exceeded your budget by ${over_amount}.
```

### 9.7.3 Skill: add-expense

**File**: `agent-capabilities/add-expense/SKILL.md`

```markdown
---
name: add-expense
description: Add a new expense with validation
---

# Add Expense

## Steps

1. Confirm with the user:
   - Amount (required)
   - Category (required, must be from their categories)
   - Date (required, default today)
   - Note (optional)
2. Validate amount with `validate_amount` hook.
3. Call `add_expense` MCP tool.
4. Confirm success with the created expense details.
5. If validation fails, explain the error and ask again.
```

### 9.7.4 Skill: budget-check

**File**: `agent-capabilities/budget-check/SKILL.md`

```markdown
---
name: budget-check
description: Check current budget status and warn if overspending
---

# Budget Check

## Steps

1. Use current month unless specified.
2. Call `get_budget_status`.
3. Report:
   - Budget amount
   - Spent so far
   - Remaining
   - Percentage used
4. If percentage > 80%, list the top 3 categories.
5. If over budget, suggest reviewing recent expenses.
6. Do not modify data.
```

### 9.7.5 Skill Discovery

| Location | Purpose |
|---|---|
| `agent-capabilities/<name>/SKILL.md` | Canonical source |
| `.agents/skills/<name>/SKILL.md` | Symlink for agent discovery |
| `.claude/skills/<name>/SKILL.md` | Symlink for Claude compatibility |

Symlinks avoid duplicating content.

### 9.7.6 How Skills Are Created

Skills are not created upfront. They emerge from doing the task first.

Process:

1. Do the task with the agent
2. Correct the agent as needed
3. At the end, ask: "Save this as a skill. Cover the workflow we
   followed and keep all the corrections I made in mind."
4. Specify: "This skill is specific to this project, so don't create
   a global skill."

## 9.8 Subagents

### 9.8.1 Subagent Structure

Subagent definitions are markdown files with YAML frontmatter, stored
in `custom-agent/<name>.md`. A symlink makes them discoverable from
`.agents/agents/`.

### 9.8.2 Subagent: finance-analyst

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

## Analysis

1. Fetch monthly summary and category breakdown.
2. Identify:
   - Categories where spending exceeds 80% of the monthly budget
   - Categories with month-over-month change > 20%
   - Transactions with amount > 2x the category average
3. Compare current month to previous 3 months.

## Output

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

- Read-only.
- Never modify data.
- Never expose raw user IDs.
```

### 9.8.3 Subagent: qa-reviewer

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
   - Check the implementation against the running app.
   - Run the relevant tests.
   - Record PASS or FAIL with evidence.
3. Run the full test suite and report results.

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
- Ignore what the implementation says it does.
- Only the acceptance criteria and running code count.
- If any criterion fails, overall verdict is FAIL.
```

### 9.8.4 Subagent Launch

| Prompt | Effect |
|---|---|
| `Launch a subagent to implement #12` | Orchestrator spawns SWE subagent |
| `Launch software engineer for #12` | Same, using named subagent definition |
| `Launch QA for #12` | Spawns QA subagent |

The subagent runs in a separate context. It sees AGENTS.md plus the
role definition but not the orchestrator's full history.

### 9.8.5 Why Separate Contexts

| Reason | Explanation |
|---|---|
| Independent verification | QA is not biased by implementation history |
| Focused attention | Each agent sees only its role and task |
| Clean context | No accumulated noise from previous tasks |
| Reproducible | Same input produces same role behavior |

## 9.9 MCP Server

### 9.9.1 Purpose

The MCP server exposes backend operations as tools that the agent can
call. It does not access the database directly. It calls the backend
API using the same JWT authentication as the frontend.

### 9.9.2 Structure

```
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
```

### 9.9.3 Server Entry

```python
# mcp-server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

from auth import verify_jwt, get_user_token
from tools import add_expense, get_budget_status, monthly_summary, list_expenses

app = Server("expense-tracker-mcp")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="add_expense",
            description="Create a new expense for the authenticated user",
            inputSchema={
                "type": "object",
                "required": ["amount", "category_id", "date"],
                "properties": {
                    "amount": {"type": "string", "pattern": "^\\d+(\\.\\d{1,2})?$"},
                    "category_id": {"type": "string", "format": "uuid"},
                    "date": {"type": "string", "format": "date"},
                    "note": {"type": "string", "maxLength": 500},
                },
            },
        ),
        Tool(
            name="get_budget_status",
            description="Get budget status for a month",
            inputSchema={
                "type": "object",
                "required": ["year_month"],
                "properties": {
                    "year_month": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                },
            },
        ),
        Tool(
            name="monthly_summary",
            description="Get category breakdown for a month",
            inputSchema={
                "type": "object",
                "required": ["year_month"],
                "properties": {
                    "year_month": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                },
            },
        ),
        Tool(
            name="list_expenses",
            description="List expenses with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "year_month": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
                    "category_id": {"type": "string", "format": "uuid"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    token = get_user_token()
    user_id = verify_jwt(token)

    if name == "add_expense":
        return await add_expense(user_id, token, arguments)
    if name == "get_budget_status":
        return await get_budget_status(user_id, token, arguments)
    if name == "monthly_summary":
        return await monthly_summary(user_id, token, arguments)
    if name == "list_expenses":
        return await list_expenses(user_id, token, arguments)

    raise ValueError(f"Unknown tool: {name}")
```

### 9.9.4 JWT Verification

```python
# mcp-server/auth.py
import os
import jwt

JWT_SECRET = os.environ["MCP_JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "expense-tracker"
JWT_AUDIENCE = "expense-tracker-api"


def verify_jwt(token: str) -> str:
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        audience=JWT_AUDIENCE,
        issuer=JWT_ISSUER,
    )
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload["sub"]


def get_user_token() -> str:
    token = os.environ.get("MCP_USER_TOKEN")
    if not token:
        raise RuntimeError("MCP_USER_TOKEN not set")
    return token
```

### 9.9.5 Tool Implementation

Tools call the backend API, not the database.

```python
# mcp-server/tools/add_expense.py
import httpx
import os

API_BASE_URL = os.environ.get("MCP_API_BASE_URL", "http://localhost:8000/api/v1")


async def add_expense(user_id: str, token: str, args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/expenses",
            json=args,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
```

### 9.9.6 Tool List

| Tool | Input | Output | Auth |
|---|---|---|---|
| add_expense | amount, category_id, date, note | Expense object | JWT |
| get_budget_status | year_month | budget, spent, remaining, percentage | JWT |
| monthly_summary | year_month | total, categories | JWT |
| list_expenses | year_month, category_id, limit | items, total | JWT |

### 9.9.7 Authentication Flow

```
pi-agent starts
  │
  ├── Reads MCP_USER_TOKEN from environment
  │
  ├── Spawns MCP server as subprocess
  │
  └── MCP server reads:
        - MCP_JWT_SECRET
        - MCP_API_BASE_URL
        - MCP_USER_TOKEN

When tool is called:
  1. MCP server retrieves token from environment
  2. Verifies JWT signature, exp, aud, iss
  3. Extracts user_id
  4. Calls backend API with Bearer token
  5. Returns structured JSON
```

### 9.9.8 Why MCP Calls API Not Database

| Reason | Explanation |
|---|---|
| Single permission layer | All authorization logic lives in the backend |
| No schema duplication | MCP does not need SQLAlchemy models |
| Same behavior as frontend | MCP uses the same endpoints |
| Easier testing | MCP can be tested against a running backend |
| Safer | MCP cannot bypass business rules |

### 9.9.9 MCP Server Launch

The MCP server is started by pi-agent as a subprocess. Configuration
is passed via environment variables.

```bash
export MCP_JWT_SECRET="same-as-backend"
export MCP_API_BASE_URL="http://localhost:8000/api/v1"
export MCP_USER_TOKEN="<user-jwt>"

pi-agent --mcp-server "python mcp-server/server.py"
```

## 9.10 Hooks

### 9.10.1 Purpose

Hooks are guardrails that run before certain agent actions. They
prevent invalid operations from reaching the backend.

### 9.10.2 Hook: validate-amount

**File**: `agent-hooks/validate-amount.py`

```python
from decimal import Decimal, InvalidOperation

MAX_AMOUNT = Decimal("1000000.00")


def validate_amount(amount: str) -> Decimal:
    """
    Validate an amount string.

    Rules:
    - Must be a valid number
    - Must be positive
    - Must not exceed MAX_AMOUNT
    - Must have at most 2 decimal places

    Raises ValueError with a clear message on failure.
    Returns the parsed Decimal on success.
    """
    try:
        value = Decimal(amount)
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

### 9.10.3 Hook: validate-ownership

**File**: `agent-hooks/validate-ownership.py`

```python
def validate_ownership(current_user_id: str, resource_user_id: str) -> None:
    """
    Verify that the current user owns the resource.

    Raises PermissionError if the resource belongs to another user.
    """
    if current_user_id != resource_user_id:
        raise PermissionError(
            "Access denied: resource belongs to another user"
        )
```

### 9.10.4 Hook Triggers

| Hook | Triggered By |
|---|---|
| validate_amount | Before creating or updating an expense via MCP |
| validate_amount | Backend Pydantic schema validation |
| validate_ownership | Before reading, updating, or deleting a resource via MCP |
| validate_ownership | Backend service layer (query filter by user_id) |

### 9.10.5 Hook README

**File**: `agent-hooks/README.md`

```markdown
# Agent Hooks

Guardrails that run before agent actions.

## validate_amount

- Trigger: before creating or updating an expense
- Checks: positive, max 1,000,000, max 2 decimal places
- On failure: raises ValueError, agent must report to user

## validate_ownership

- Trigger: before reading, updating, or deleting a resource
- Checks: resource.user_id == current_user.id
- On failure: raises PermissionError

## Design Notes

- Hooks are pure functions with no side effects.
- Hooks do not access the database. They only validate inputs.
- Hooks are also enforced in the backend for defense in depth.
```

## 9.11 Permissions

### 9.11.1 Permissions Matrix

**File**: `docs/permissions.md`

```markdown
# Permissions

## User Roles

| Role | Description |
|---|---|
| User | Regular authenticated user |
| System | Backend service |

## Resource Permissions

| Resource | User | System |
|---|---|---|
| Own expenses | Read/Write | Read/Write |
| Other users' expenses | None | Read/Write |
| Own budgets | Read/Write | Read/Write |
| Other users' budgets | None | Read/Write |
| System categories | Read | Read/Write |
| Own categories | Read/Write | Read/Write |
| Audit logs | None | Read/Write |

## Agent Permissions

| Agent | Read Expenses | Write Expenses | Read Budgets | Write Budgets | Read Audit |
|---|---|---|---|---|---|
| finance-analyst | Own | None | Own | None | None |
| qa-reviewer | Test data | Test data | Test data | Test data | None |
| MCP add_expense | None | Own | None | None | None |
| MCP get_budget_status | Own | None | Own | None | None |
| MCP monthly_summary | Own | None | Own | None | None |
| MCP list_expenses | Own | None | None | None | None |

## Enforcement

- Backend: all queries filter by `user_id`
- MCP: JWT verification, user_id from token
- Hooks: `validate_ownership` before resource access
- Tests: `test_isolation.py` verifies cross-user access returns 404

## Escalation

- Agent cannot modify system categories
- Agent cannot access audit logs
- Agent cannot delete user accounts
- Agent cannot change permissions
- Agent cannot access other users' data
```

### 9.11.2 Defense in Depth

| Layer | Enforcement |
|---|---|
| Hook | Validates before the call |
| MCP | Verifies JWT, extracts user_id |
| Backend dependency | Loads current user from token |
| Backend service | Filters queries by user_id |
| Backend test | Verifies cross-user access returns 404 |
| Database | Foreign keys and constraints |

## 9.12 Real Session Records

### 9.12.1 Why Record Sessions

Criterion 2 requires evidence that AI tools were actually used. Real
session records show:

- What prompts were given
- What the agent produced
- What was corrected
- What was verified

### 9.12.2 Session Record Format

Each session entry in `docs/ai-workflow.md` follows this format:

```markdown
## Session: <task>

**Date**: YYYY-MM-DD
**Tool**: pi-agent + qwen3.8-27b
**Prompt**: `<the prompt>`

**Agent Output**:
- What the agent did

**Human Review**:
- What was checked
- What was corrected

**Commit**: `<commit message>`
```

### 9.12.3 Example: Groom Issue #12

```markdown
## Session: Groom issue #12

**Date**: 2026-10-08
**Tool**: pi-agent + qwen3.8-27b
**Prompt**: `Groom issue #12`

**Agent Output**:
- Rewrote issue with 14 acceptance criteria
- Added out-of-scope items: bulk delete → #20, search → #21
- Added constraints: Decimal, user_id filter, follow openapi.yaml

**Human Review**:
- Checked acceptance criteria are testable
- Added "audit log written" as a criterion
- Approved

**Commit**: `docs: groom issue #12`
```

### 9.12.4 Example: Implement Issue #12

```markdown
## Session: Implement issue #12

**Date**: 2026-10-09
**Tool**: pi-agent + qwen3.8-27b
**Prompt**: `Implement issue #12`

**Agent Output**:
- Created 4 endpoints in `backend/app/routers/expenses.py`
- Created service layer in `backend/app/services/expense_service.py`
- Created Pydantic schemas in `backend/app/schemas/expense.py`
- Wrote 18 tests in `backend/tests/integration/test_expenses_api.py`
- All tests pass

**Human Review**:
- Checked OpenAPI alignment
- Verified user_id filter in every query
- Verified Decimal usage
- Ran tests locally: 18 passed

**Commit**: `abc1234 feat(expenses): implement CRUD endpoints`
```

### 9.12.5 Example: QA Fail and Fix

```markdown
## Session: QA issue #12

**Date**: 2026-10-09
**Tool**: pi-agent + qwen3.8-27b
**Prompt**: `Test issue #12`

**Agent Output**:
- Verdict: FAIL
- 13/14 criteria PASS
- 1 criterion FAIL: DELETE other user's expense returned 204 instead of 404
- Root cause: missing user_id filter in delete_expense()

**Human Review**:
- Confirmed the bug is real
- Sent back to SWE with the QA comment

## Session: Fix issue #12

**Date**: 2026-10-09
**Prompt**: `Fix issue #12 based on QA comment`

**Agent Output**:
- Added user_id filter to delete_expense()
- Added test: test_delete_other_user_expense_returns_404
- 46 tests pass

**Commit**: `def5678 fix(expenses): add user_id filter to delete`

## Session: Re-verify issue #12

**Date**: 2026-10-09
**Prompt**: `Test issue #12`

**Agent Output**:
- Verdict: PASS
- All 14 criteria PASS

**Orchestrator**: Closed issue #12
```

### 9.12.6 Session Record Coverage

| Phase | Sessions Recorded |
|---|---|
| Spec | Grooming of 30+ issues |
| Auth | Register, login, me |
| CRUD | Categories, expenses, budgets |
| Dashboard | Summary, by-category, trend, cumulative, heatmap, recent |
| Frontend | Each page and chart |
| Testing | Unit, integration, E2E |
| Security | Scan execution and review |
| Deployment | Render deploy and verification |

## 9.13 Correction Log

### 9.13.1 Purpose

The correction log records mistakes the agent made and how they were
fixed. This shows the human review process is real.

### 9.13.2 Format

| Date | Issue | AI Output | Correction | Lesson |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### 9.13.3 Example Entries

| Date | Issue | AI Output | Correction | Lesson |
|---|---|---|---|---|
| 2026-10-09 | #12 | Pagination allowed page=0 | Added `Query(ge=1)` | Specify validation in acceptance criteria |
| 2026-10-10 | #14 | Amount used float | Changed to Decimal | Add to constraints: "use Decimal for money" |
| 2026-10-11 | #15 | Category filter returned other users' categories | Added user_id filter | Add isolation test to every endpoint issue |
| 2026-10-12 | #18 | Dashboard aggregation returned float sum | Cast to Decimal, quantize | Aggregation must return Decimal |
| 2026-10-13 | #22 | Heatmap started on Sunday | Changed to Monday start | Specify week start in acceptance criteria |
| 2026-10-14 | #25 | Delete category allowed with expenses | Added CATEGORY_IN_USE check | Specify referential integrity in constraints |

### 9.13.4 Document Updates

When a correction reveals a missing rule, the rule is added to the
relevant document:

| Correction | Document Updated |
|---|---|
| Decimal for money | AGENTS.md, docs/team/software-engineer.md |
| user_id filter | AGENTS.md, docs/testing-guidelines.md |
| Monday week start | docs/design-system.md, docs/testing-guidelines.md |
| Pagination validation | docs/task-template.md |

## 9.14 Data Policy

### 9.14.1 Policy Summary

**File**: `security/ai-tool-data-policy.md`

All code, prompts, and context stay on the local machine. No data is
sent to cloud LLM providers.

### 9.14.2 What the Agent Sees

| Data Type | Agent Access | Notes |
|---|---|---|
| Source code | Yes | Needed to implement tasks |
| Test files | Yes | Needed to write and run tests |
| Documentation | Yes | Needed for context |
| OpenAPI spec | Yes | Needed for backend work |
| Seed data | Yes | Test categories only |
| Real user data | No | Never used in development |
| Production database | No | Never connected |
| Secrets (.env) | No | Not included in context |
| JWT tokens | No | Not included in context |

### 9.14.3 What the Agent Produces

| Output | Review Required |
|---|---|
| Code | Yes, against acceptance criteria |
| Tests | Yes, must pass |
| Commits | Yes, message must follow convention |
| Documentation | Yes, must be accurate |
| Security notes | Yes, human review |

### 9.14.4 Data Flow

```
Developer machine
  │
  ├── Source code ────────▶ pi-agent (local)
  ├── Documentation ──────▶ pi-agent (local)
  ├── Test data ──────────▶ pi-agent (local)
  │
  └── No data leaves the machine

No connection to:
  - Cloud LLM APIs
  - External AI services
  - Production databases
```

### 9.14.5 Compliance Notes

| Concern | Handling |
|---|---|
| Data residency | All local, no cross-border transfer |
| PII | Not present in development data |
| Secrets | Never included in agent context |
| Audit | Session records in docs/ai-workflow.md |
| Reproducibility | Same model version across sessions |

## 9.15 AI Workflow Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Primary agent | pi-agent | Local, controllable, supports needed capabilities |
| Model | qwen3.8-27b | Local, no API cost, sufficient for task size |
| Context file | AGENTS.md | Tool-agnostic, read at every session |
| Claude compat | CLAUDE.md with `@AGENTS.md` | Single line, no duplication |
| Roles | PM, SWE, QA | Matches course Part 1 |
| Orchestration | Main session | Enforces the graph |
| Backlog | GitHub Issues | Canonical, trackable |
| Execution | Sequential | Simpler than parallel for MVP |
| Skills | 3 (report, add, check) | Cover the main agent use cases |
| Subagents | 2 (analyst, QA) | Separate contexts for analysis and verification |
| MCP tools | 4 | Read and write operations |
| MCP auth | JWT | Same as backend |
| MCP data access | Via API, not database | Single permission layer |
| Hooks | 2 (amount, ownership) | Prevent invalid operations |
| Loop | `/goal` command | Keeps orchestrator running |
| Session records | Real, in docs/ai-workflow.md | Evidence for Criterion 2 |
| Data policy | Local only | Privacy, no cloud dependency |
```

---

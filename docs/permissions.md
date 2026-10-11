# Permissions

The access matrix for this project (REQ-EXT-060, REQ-AI-100): who may do
what, which artifact enforces it, what is forbidden outright, and how a
violation escalates. The companion overview of the whole extension pack is
[docs/agent-extension-pack.md](agent-extension-pack.md); this document is
kept as its own file by REQ-EXT-083.

## Measured Component Counts

The pack described here ships (REQ-AI-143):

- Skills: 3
- Hooks: 2
- MCP tools: 4
- Subagents: 2

## User Roles

The merged `users` model (`backend/app/models/user.py`) carries no admin or
group column, so the application models exactly two roles:

| Role | How obtained | What it can do |
| --- | --- | --- |
| Anonymous | no token | `GET /api/v1/health` and the auth register/login routes only |
| Authenticated user | a valid access token from the auth routes | the full expense, category, budget, and dashboard surface — scoped to their own rows |

There is deliberately no superuser role: an agent acting for a user holds
that user's privileges and nothing more.

## Resource Permissions

Per endpoint family (all prefixes under `/api/v1`):

| Resource family | Anonymous | Authenticated user |
| --- | --- | --- |
| `GET /health` | allowed | allowed |
| `/auth/register`, `/auth/login` | allowed | allowed |
| `/auth/me` | 401 | own profile |
| `/expenses` (CRUD) | 401 | own expenses only (`Expense.user_id == user.id`) |
| `/categories` | 401 | seeded system categories, own custom rows |
| `/budgets` | 401 | own budgets only |
| `/dashboard/summary`, `/dashboard/by-category` | 401 | aggregates over own rows only |

Ownership is not a "permission check" bolted on top: the service layer
filters every query by the authenticated user, so cross-owner access is
unreachable rather than merely refused.

## Agent Permissions

The MCP server is not a principal. It authenticates as one human user via
`MCP_USER_TOKEN` and can therefore do exactly what that user's own session
could do — no more (REQ-ARCH-002):

| Agent surface | Permission |
| --- | --- |
| `add_expense` tool | create one expense for the token's owner (guardrail first) |
| `list_expenses` tool | read the token owner's expenses |
| `get_budget_status` tool | read the token owner's budget status |
| `monthly_summary` tool | read the token owner's category breakdown |
| any other endpoint | not exposed; the frozen four-endpoint map refuses it |
| direct database access | none — the server has no connection string |
| admin or impersonation scope | none — `verify_jwt` checks the caller, not a role |

## Skill Permissions

What each of the three skills may do, and what it must call first:

| Skill | Read | Write | Precondition |
| --- | --- | --- | --- |
| add-expense | — | one expense row | `validate_amount` hook must pass before the call |
| budget-check | budget status | none | read-only, report and warn only |
| monthly-report | month totals, category rows | none | read-only; line detail only on request |

## Subagent Permissions

What each of the two subagents may do (REQ-EXT-040):

| Subagent | Read | Write | Rule |
| --- | --- | --- | --- |
| finance-analyst | expenses, budgets, summaries | none | read-only analyst: recommends, never applies |
| qa-reviewer | issue text, branch, verification output | none | reports PASS/FAIL with executed evidence; do not fix |

Neither subagent receives credentials, and neither may modify, stage,
commit, or push any repository artifact during a run.

## Enforcement Layers

Defense in depth (REQ-AI-101, REQ-EXT-025): six layers, each enforced by a
real artifact in this repository — a failure at one layer is caught by the
next.

| Layer | Enforcing artifact | What it enforces |
| --- | --- | --- |
| Hook (agent-side guardrail) | `agent-hooks/validate-amount.py` | amount present, positive, finite, <= 999999999.99, two decimals |
| MCP (transport and auth gate) | `mcp-server/auth.py` | JWT signature, expiry, audience, issuer, `type == "access"` before any dispatch |
| Backend dependency | `backend/app/auth/dependencies.py` | `get_current_user` resolves the caller or answers 401 |
| Backend service | `backend/app/services/expense_service.py` | `AMOUNT_MAX` money rules and per-user ownership filtering |
| Backend test | `backend/tests/integration/test_agent_hooks.py` | hook rules and backend rules provably agree (14 nodes) |
| Database | `backend/alembic/versions` (FK migration surface) | `NUMERIC(12,2)` scale, `NOT NULL`, FK constraints with `ondelete` |

The hook layer is the only agent-side layer; layers three to six are
server-side and remain the authority — a bypassed hook still fails at the
API, and a bypassed API still fails at the database.

## Forbidden Actions

No agent, skill, hook, or subagent may:

- connect to, read, or write the database directly — the only data path is
  the public HTTP API (the MCP server carries no ORM or connection string);
- import the backend application or add a backend route to widen the agent
  surface beyond the frozen four endpoints;
- mutate another user's rows — ownership is filtered at the service layer;
- bypass a hook: `validate_amount` and `validate_ownership` raise, and the
  error must be surfaced, never swallowed;
- fix code during a review or analysis run — the qa-reviewer reports
  failures, the finance-analyst only recommends;
- receive, store, or request credentials or raw record identifiers in
  prompts, reports, or skill text;
- perform destructive bulk operations: the pack exposes no delete tool at
  all, so deletion stays a human UI action.

## Escalation Rules

How a violation surfaces and who owns the next step:

1. Hook rejection: the guardrail raises `ValueError` / `PermissionError`;
   the agent stops and reports the error to the user — it does not retry
   with a modified value.
2. API refusal: a non-2xx answer becomes `McpToolError` and is reported
   verbatim; the agent does not attempt a different route to the same data.
3. Policy violation observed by a reviewer run: the qa-reviewer records a
   FAIL verdict with the executed command and exit code, posts it back to
   the orchestrator, and stops — repair is builder work, never reviewer
   work.
4. Read-only analyst findings: the finance-analyst posts suggested
   adjustments as advisory text only; a human decides whether to apply them.
5. Suspected guardrail bypass: treated as a security incident for the human
   maintainer — the backend and database layers still refuse the operation,
   and the issue is escalated rather than auto-mitigated.
6. Unresolvable ambiguity in a policy: the agent writes it up as a blocker
   for a human decision instead of guessing a privilege it was not granted.

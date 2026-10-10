# Agent Extension Pack

This document describes the reusable capabilities that extend the base
coding agent for this project, in one place, for a reviewer (REQ-EXT-050).
The pack is five components (REQ-EXT-001): skills, hooks, an MCP server,
subagents, and this documentation itself. In numbers the pack ships three
skills, two hooks, four MCP tools, and two subagents (REQ-AI-143), plus the
permissions matrix at [docs/permissions.md](permissions.md).

Every count and path below is facts-derived from the merged tree: the count
block is computed from the real directories with the same recipes the
component cards pin, so the prose and the measurement can never drift.

## Measured Component Counts

- Skills: 3
- Hooks: 2
- MCP tools: 4
- Subagents: 2

| Component | Directory | Purpose |
| --- | --- | --- |
| Skills | `agent-capabilities/` | Repeatable procedures |
| Hooks | `agent-hooks/` | Input guardrails |
| MCP Server | `mcp-server/` | Backend tools over the public API |
| Subagents | `custom-agent/` | Specialized read-only agents |
| Permissions | `docs/permissions.md` | Access matrix |

## Skills

Three skills live under `agent-capabilities/`, one directory per skill, each
with a `SKILL.md` carrying YAML frontmatter (`name`, `description`) and the
pinned section set:

| Skill | Purpose |
| --- | --- |
| add-expense | Record an expense, validating the amount first |
| budget-check | Report budget usage and warn at 80% or over |
| monthly-report | Produce a monthly spending report with top categories |

Skills are procedures, not code: each `SKILL.md` describes when to use it,
the steps (which MCP tool to call in which order), the output template, and
the guardrails. The add-expense skill must run the `validate_amount` hook
before any call; the budget-check and monthly-report skills are read-only —
they report and warn, they never change data.

## Hooks

Two standalone guardrail hooks live in `agent-hooks/` as plain
standard-library modules (no package, no I/O, no network):

| Hook | Purpose |
| --- | --- |
| `validate-amount.py` | Reject invalid amounts before an expense is created |
| `validate-ownership.py` | Reject access to another user's resources |

Both hooks raise on violation (`ValueError` / `PermissionError`); the agent
must surface the error, never swallow it. The same rules are re-enforced in
the backend schema, service, and database layers, so a bypassed hook still
fails at the API — see the enforcement-layer table in
[docs/permissions.md](permissions.md).

## MCP Server

The MCP server (`mcp-server/`) is a stdio JSON-RPC process the agent spawns;
it exposes four MCP tools, each pinned to one frozen backend endpoint:

| Tool | Method and path | Purpose |
| --- | --- | --- |
| add_expense | `POST /expenses` | Create one expense (guardrail first) |
| get_budget_status | `GET /dashboard/summary` | Simplified budget status |
| monthly_summary | `GET /dashboard/by-category` | Per-category month breakdown |
| list_expenses | `GET /expenses` | List expenses with filters and pagination |

The core (`server.py`, `auth.py`, `config.py`) answers `initialize`,
`tools/list`, and `tools/call`; the four tool modules under
`mcp-server/tools/` perform the single frozen HTTP request each. See
`mcp-server/README.md` for the full operational contract.

## Subagents

Two subagent definitions live in `custom-agent/`, both read-only:

| Subagent | Purpose |
| --- | --- |
| finance-analyst | Analyze a month's spending against budgets; never writes |
| qa-reviewer | Verify a change against its acceptance criteria; never fixes |

Both run in a fresh context with no orchestrator history and post their
report back. The launch commands (REQ-EXT-043) are:

1. Launch finance analyst for 2026-10
2. Launch QA for #36

## Discovery

Canonical directories and the `.agents/` discovery surface (REQ-EXT-080):
the authoritative files live in `agent-capabilities/`, `agent-hooks/`,
`mcp-server/`, and `custom-agent/`; the agent-facing discovery paths are
`.agents/skills/` and `.agents/agents/`, which hold git symlinks (mode
`120000`) pointing back at the canonical files
(`../../agent-capabilities/<name>/SKILL.md` and
`../../custom-agent/<name>.md`). Editing the canonical file is enough — the
symlinked discovery path always shows the same bytes.

Three discovery modes (REQ-EXT-014):

1. Auto-discovery at session start: the agent reads `.agents/skills/` and
   `.agents/agents/` and loads each frontmatter.
2. Natural-language invocation: describe the task ("summarize my October
   spending") and the agent picks the matching skill.
3. Explicit command: name the skill or subagent directly, e.g. "Use the
   monthly-report skill for 2026-10", "Launch finance analyst for 2026-10",
   or "Launch QA for #36".

## Design Principles

- One data path: every agent read or write goes through the public HTTP API
  with a real JWT — the MCP server is not the database, it never touches the
  database directly, never imports the backend application, and never adds a
  backend route (REQ-ARCH-002, REQ-AI-087).
- MCP transport is stdio: the agent spawns the server as a subprocess and
  exchanges newline-delimited JSON-RPC over stdin/stdout — no port, no
  listener, no daemon (REQ-EXT-081).
- Auth is JWT: `verify_jwt` checks signature, expiry, audience, issuer and
  the `type == "access"` claim before any tool dispatch, mirroring the
  backend dependency (REQ-AI-083).
- Hooks are guardrails, not authority: they fail early and loudly, but the
  server-side layers remain the enforcement point (REQ-AI-101).
- Read-only analyst, non-fixing reviewer: the finance-analyst only reads and
  recommends, and the qa-reviewer is told to do not fix — it reports
  failures with executed evidence and leaves repair to the builder
  (REQ-EXT-082, REQ-EXT-040).
- Skills are procedures in Markdown, not executable code, so they are
  reviewable and portable across agent hosts.

## Directory Choices

| Path | Why here (REQ-EXT-080) |
| --- | --- |
| `agent-capabilities/` | Canonical skill bodies, one directory per skill |
| `.agents/skills/` | Host discovery path: symlinks to the canonical skills |
| `agent-hooks/` | Flat, dependency-free guardrail modules |
| `mcp-server/` | Self-contained stdio server, separate from the backend app |
| `custom-agent/` | Canonical subagent cards |
| `.agents/agents/` | Host discovery path: symlinks to the canonical cards |
| `docs/agent-extension-pack.md` | This overview (REQ-EXT-083: separate file) |
| `docs/permissions.md` | The access matrix, kept as its own document |

## MCP Design Choices

REQ-EXT-081, as landed in the merged `mcp-server/`:

- stdio transport, newline-delimited JSON-RPC 2.0, protocol `2024-11-05`;
  no SDK and no network listener.
- Exactly four tools on four frozen endpoint pairs; a fifth tool or an
  unrelated path breaks the pinned contract.
- JWT bearer auth end to end: the same access token the frontend uses;
  `MCP_JWT_SECRET`, `MCP_API_BASE_URL`, and `MCP_USER_TOKEN` are the only
  configuration.
- API, not database: tools use httpx against the merged API; the server
  carries no ORM, no connection string, and no SQL.
- Strict input schemas (`additionalProperties: false`) so malformed calls
  are refused before dispatch, and three distinct failure classes
  (`AuthError`, `ValueError`, `McpToolError`).

## Permissions

The full access matrix lives in [docs/permissions.md](permissions.md); this
section is a pointer plus the summary rows, not a restatement (REQ-EXT-083).

- Users: every non-public endpoint requires a valid JWT; data is isolated
  per owner.
- Agents: the MCP server holds no privileges of its own — it acts as its
  bearer token's user and can do nothing that user could not do in the UI.
- Subagents and skills: read-only except add-expense, which writes only
  through the validated single-record path.
- Enforcement: six defense-in-depth layers, listed with their enforcing
  artifacts in the permissions document.

## Criterion 12

REQ-EXT-002 mapping — where each required artifact lives:

| Criterion 12 item | Artifact |
| --- | --- |
| project instructions | `AGENTS.md` plus the role skills under `skills/` |
| reusable workflow | the three skills in `agent-capabilities/` |
| subagent | `custom-agent/finance-analyst.md`, `custom-agent/qa-reviewer.md` |
| MCP tool and MCP server | `mcp-server/tools/` (four tools) and `mcp-server/server.py` |
| hook guardrail | `agent-hooks/validate-amount.py`, `agent-hooks/validate-ownership.py` |
| permission notes | [docs/permissions.md](permissions.md) |

## Verification Checklist

One copyable line per component (REQ-EXT-070); each is a real gate recipe
from the component cards, and t35 re-executes them (REQ-EXT-071). Run from
the repository root.

- Skills: `find agent-capabilities -mindepth 2 -maxdepth 2 -type f -name SKILL.md | wc -l` — expect 3
- Hooks: `find agent-hooks -maxdepth 1 -type f | grep -v README.md` — expect the 2 guardrail modules
- MCP server and tools: `find mcp-server/tools -maxdepth 1 -type f -name *.py | grep -v __init__.py` — expect the 4 tool modules; the core lives alongside in `mcp-server/`
- Subagents: `find custom-agent -maxdepth 1 -type f -name *.md | wc -l` — expect 2
- Skills symlink discovery: `git ls-files -s .agents/skills` — expect 3 entries, all mode 120000
- Agents symlink discovery: `git ls-files -s .agents/agents` — expect 2 entries, all mode 120000
- Documentation: `test -f docs/agent-extension-pack.md && test -f docs/permissions.md && echo documentation present` — both pack docs exist as separate files

## Related Documents

- [docs/permissions.md](permissions.md) — the permissions matrix (REQ-EXT-060)
- `mcp-server/README.md` — MCP operational contract
- `agent-hooks/README.md` — hook trigger points and failure behavior

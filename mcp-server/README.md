# Expense Tracker MCP server

A stdio Model Context Protocol server that lets an AI agent read and write the
expense tracker through its **public HTTP API** — the same endpoints, the same
credentials and the same authorization rules the frontend uses. It is not a
second data path: it never connects to the database, never imports the backend
application and never adds a route of its own (REQ-AI-087, REQ-ARCH-002).

## Layout

| File | Owner | Role |
| --- | --- | --- |
| `config.py` | t31 | Reads the three environment variables, re-states the JWT constants |
| `auth.py` | t31 | `verify_jwt()` (signature/expiry/audience/issuer/type) and `get_user_token()` |
| `server.py` | t31 | Newline-delimited JSON-RPC loop: `initialize`, `tools/list`, `tools/call` |
| `tools/add_expense.py` | t32 | Guardrail first, then `POST /expenses` |
| `tools/get_budget_status.py` | t32 | `GET /dashboard/summary`, simplified four-key answer |
| `tools/monthly_summary.py` | t32 | `GET /dashboard/by-category`, per-category rows |
| `tools/list_expenses.py` | t32 | `GET /expenses` with filters and pagination |
| `tools/__init__.py` | t32 | `McpToolError`, the single failure type of the tool layer |

`pyproject.toml` is a declaration only: the server needs nothing beyond what the
merged backend environment already provides (`httpx`, `python-jose`).

## Tools

Four tools, four frozen endpoints, one request each (REQ-AI-085, REQ-EXT-034..037):

| Tool | Method and path | What it returns |
| --- | --- | --- |
| `add_expense` | `POST /expenses` | The created expense, ten keys |
| `get_budget_status` | `GET /dashboard/summary` | `total_spent`, `total_budget`, `remaining`, `percentage` |
| `monthly_summary` | `GET /dashboard/by-category` | `year_month`, `total`, the `categories` rows |
| `list_expenses` | `GET /expenses` | The `{items, total, page, page_size}` envelope |

`list_expenses` translates the agent-facing parameters onto the API's query
names: `limit` maps to `page_size`, `category` maps to `category_id` and `month`
maps to `year_month`. `get_budget_status` deliberately returns the simplified
shape rather than the raw upstream body, so the agent surface stays small.

Every input schema is strict: typed properties, an explicit required list and
`additionalProperties: false`, so a malformed call is refused before any
dispatch (REQ-AI-082).

## Authentication

The agent authenticates exactly as the frontend does — with an access token
minted by the backend's own auth routes:

1. A human signs in through the normal login flow and copies an access token.
2. The token is handed to the server as `MCP_USER_TOKEN` when it is launched.
3. `get_user_token()` supplies that token and `verify_jwt()` checks the
   signature, expiry, audience, issuer and `type == "access"` claim.
4. Each tool sends `Authorization: Bearer <token>` on its single request.

The JWT check happens **before** any tool is dispatched, so an unverified caller
cannot reach a tool module or the network at all. Failures are never swallowed:
`AuthError` for authentication, `ValueError` for bad parameters or a rejected
guardrail, `McpToolError` for a non-2xx API answer (REQ-AI-083/084).

## Environment variables

| Variable | Meaning |
| --- | --- |
| `MCP_JWT_SECRET` | Shared HS256 secret, identical to the backend's `JWT_SECRET` |
| `MCP_API_BASE_URL` | Base URL of the merged API, e.g. `http://localhost:8000/api/v1` |
| `MCP_USER_TOKEN` | The bearer access token the server presents to that API |

All three are read once, at import, by `config.py`. The secret and the base URL
must match the running backend; the token expires on the backend's own schedule
(24 hours by default) and the server refuses to authenticate anything until the
operator supplies a real value.

## Running

The server is a **subprocess** that speaks JSON-RPC over its own stdin/stdout —
the agent spawns it, writes one request per line and reads one response per
line. There is no port, no listener and no daemon to supervise. Register it in
the agent's MCP configuration with all three variables in the launch
environment:

```bash
MCP_JWT_SECRET=... MCP_API_BASE_URL=http://localhost:8000/api/v1 MCP_USER_TOKEN=<token> \
  python server.py
```

The equivalent registration entry for a desktop MCP client:

```json
{
  "mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "MCP_JWT_SECRET": "<shared jwt secret>",
        "MCP_API_BASE_URL": "http://localhost:8000/api/v1",
        "MCP_USER_TOKEN": "<bearer access token>"
      }
    }
  }
}
```

Because the launch environment is the only configuration channel, a per-user
token never has to be written to disk.

## Design notes

- **stdio, not HTTP.** The MCP transport is the process's own stdin/stdout, so
  the server needs no socket, no TLS and no lifecycle of its own; a crashed
  agent simply stops spawning it (REQ-AI-080, REQ-EXT-081).
- **API, not the database.** Tools call the merged REST API and never touch the
  database: the API's own validation, ownership checks and audit logging stay
  in force for agent traffic, which is why no agent-only endpoint exists
  (REQ-AI-087, REQ-ARCH-002).
- **JWT verification locally, before dispatch.** Verifying the token in the
  server gives an immediate, explicit rejection instead of a confusing upstream
  401, and it keeps the guardrail in front of every tool (REQ-AI-082/083).
- **Guardrails before requests.** `add_expense` runs the t30
  `validate-amount.py` hook by path before it builds the payload, so a rejected
  amount never produces a request; the hook's rules mirror the backend's money
  rules exactly, so the two layers can never disagree (REQ-AI-091, REQ-AI-093).
- **One request per tool, on a frozen path.** The four `(method, path)` pairs
  are fixed by the server core; a tool that wanted a fifth endpoint would be a
  new requirement, not a code change.
- **Tests live in the backend suite.** `backend/tests/integration/test_mcp_tools.py`
  drives the tools in-process against an `httpx.MockTransport`, so the whole
  vertical — token acceptance, rejection before dispatch, non-2xx handling,
  guardrail rejection and the exact request shape — is executed with zero
  network egress (REQ-PLAN-061).

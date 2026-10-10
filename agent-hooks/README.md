# Agent Hooks

Two standalone guardrail hooks — `validate-amount.py` and
`validate-ownership.py` — that run as pure functions before agent actions
(REQ-AI-090). They are plain modules, not a package: no `__init__.py`, no
dependencies beyond the standard library, no I/O, and no network access.
The hyphenated file names are pinned by the requirements, so tests reach
them through an importlib file loader rather than an import statement.

Both hooks exist so an AI agent driving this repository over MCP cannot
perform an action the HTTP API itself would refuse. The backend half of
the same rules is already enforced by the merged Pydantic schema and
service layer, so the hooks are an early, in-process guardrail — never a
replacement for server-side validation.

## Trigger

Each hook runs before every MCP tool call that creates or mutates an
expense, and the same rules are re-enforced in the backend after the call
reaches the API:

- `validate_amount(value)` — before every MCP tool call that sends an
  `amount`, and again in the backend schema layer (`AMOUNT_MAX` in
  `backend/app/schemas/expense.py`) and service layer
  (`AMOUNT_MAX` in `backend/app/services/expense_service.py`).
- `validate_ownership(owner_id, user_id)` — before every MCP tool call
  that reads or mutates a single resource, and again in the backend,
  where the `get_current_user` dependency in
  `backend/app/auth/dependencies.py` resolves the caller and the service
  filters every query by `Expense.user_id == user.id`.

A hook therefore fires first; the schema, service, and database layers
remain the authority. If a hook is ever bypassed, the request still fails
at the API.

## Checks

`validate_amount(value: object) -> Decimal` accepts a present, valid,
finite number that is strictly positive, at most `MAX_AMOUNT`
(`Decimal("999999999.99")`, equal to the backend's `AMOUNT_MAX`), and
carries at most two decimal places. It rejects `None`, the empty string,
non-numeric strings, booleans, non-numeric objects, zero, negatives,
values above the ceiling, and over-precise values. On success it returns
the amount as a `Decimal`.

`validate_ownership(owner_id: object, user_id: object) -> None` checks
that both ids are present and equal. It performs no lookup of its own; the
caller passes the owner id it already loaded and the authenticated id
from the token.

## Failure behavior

Both hooks raise; neither returns an error object, writes a log line, nor
swallows a violation.

- `validate_amount` raises `ValueError` for every rejected amount, which
  the MCP layer surfaces as a tool error, mirroring the API's `422`
  `INVALID_AMOUNT` response.
- `validate_ownership` raises `PermissionError` when either id is `None`
  and when the ids differ, mirroring the API's `404`/`403` isolation
  behavior.

Nothing is persisted on the failure path: no row is written, no partial
object is returned, and no exception is caught inside the hooks.

## Agent behavior

An agent receiving a hook exception must not retry the same call with the
same arguments. The expected behavior is to report the rejection to the
user with the hook's message, correct the input (for example round an
amount to two decimals, or drop a request for another user's resource),
and re-issue the tool call only if the corrected request is what the user
asked for. An agent must never disable, edit, or skip a hook to get a
call through, and must never treat a passing hook as permission to skip
backend validation — the backend answer is final.

## Design notes

- Hooks are pure functions with no side effects (REQ-EXT-020), which is
  what lets `backend/tests/integration/test_agent_hooks.py` import and
  exercise them directly in the ordinary test run.
- Defense in depth (REQ-AI-101 / REQ-EXT-025) — the six layers, in order:
  hook, MCP, backend schema, backend service, backend test, database.
  This card lands the hook layer and the backend test that attests to the
  others; it does not claim ownership of the MCP, schema, service, or
  database layers.
- `MAX_AMOUNT` is asserted equal to the imported backend `AMOUNT_MAX` in
  the test suite, so the guardrail and the schema can never drift apart
  silently. The ceiling is the `NUMERIC(12,2)` capacity, `999999999.99`.
- `validate-ownership.py` imports nothing at all, and
  `validate-amount.py` imports only `decimal`. That constraint is
  enforced by the card's verification gates, not by convention.
- Wiring the hooks into the MCP call path belongs to the MCP tools card;
  this card owns the functions and their tests only.

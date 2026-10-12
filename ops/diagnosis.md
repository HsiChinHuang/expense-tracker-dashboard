# Diagnosis Worked Example

The REQ-OPS-040..048 worked example for the Expense Tracker Dashboard: one
real scenario carried end to end - symptom, steps, expected output copied
from a REAL measured run, expected behavior, verification, recovery,
findings and lessons. The steps below were executed against the local
backend on `127.0.0.1:8137` (the verification endpoint pinned by the t41
gate; the deployed endpoint is `https://expense-tracker-dashboard.onrender.com`
and its live comparison is carried as the `LIVE_DEPLOYMENT_STATE` deferral
row in `docs/criteria/security_ops_verification.md`). When a step's output
does not match, escalate to the numbered symptom sections of
`ops/runbook.md` - this file is the worked example, the runbook is the
decision tree.

## Scenario

A user reports the dashboard "is not loading their data". The operator's
first stop is the public health endpoint; the documented scenario
(Chapter 13 §13.5, REQ-OPS-041) is a database layer that stopped answering
within the 5-second connect budget, so `create_db_engine`
(`backend/app/database.py`, REQ-BE-130/133) fell back to SQLite at startup
and `/api/v1/health` began reporting `"status": "degraded"` with
`"fallback_active": true`. The fallback flow is startup-only: the flag is
latched once by `create_db_engine` and never re-probed per request, so
recovery requires a restart after the primary database is reachable again
(FR-DB-1). This file reproduces the healthy baseline of that flow with
real measured output; the degraded half of the flow is attested by the
merged t25/t28 fallback evidence and the runbook's database sections.

## Diagnosis Steps

Run each command from the repository root and compare its output against
the Expected Output section below. The health probe is the entry point;
steps 2-6 are the smoke sequence (register, login, category, expense,
list, dashboard summary) that proves the data path end to end.

```bash
curl -fsS http://127.0.0.1:8137/api/v1/health
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8137/api/v1/auth/register -H "Content-Type: application/json" -d "{\"email\":\"t41diag@example.com\",\"username\":\"t41diag\",\"password\":\"verification123\"}"
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8137/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"t41diag@example.com\",\"password\":\"verification123\"}"
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8137/api/v1/categories -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{\"name\":\"Diagnosis Groceries\",\"color\":\"#EF4444\"}"
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8137/api/v1/expenses -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{\"category_id\":\"$CATEGORY_ID\",\"amount\":\"12.34\",\"date\":\"2026-10-12\",\"note\":\"t41 diagnosis smoke\"}"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8137/api/v1/expenses -H "Authorization: Bearer $TOKEN"
curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8137/api/v1/dashboard/summary?year_month=2026-10" -H "Authorization: Bearer $TOKEN"
```

`$TOKEN` is the `access_token` value returned by the login call and
`$CATEGORY_ID` the `id` returned by the category call; the verification
gate captures both from the live JSON bodies.

## Expected Output

Copied from the real measured run of 2026-10-12 against the local backend
(`DATABASE_URL` pointed at a scratch SQLite file, `uv run alembic upgrade
head` first, uvicorn on 127.0.0.1:8137, torn down afterwards):

```json
{"status":"ok","database":"sqlite","fallback_active":false,"version":"0.1.0"}
```

Step status codes measured in the same run: register `201`, login `200`,
category create `201`, expense create `201`, expense list `200` (the list
body contains the created note `t41 diagnosis smoke`), dashboard summary
`200` with the body:

```json
{"year_month":"2026-10","total":"12.34","budget_amount":"0.00","remaining":"-12.34","percentage":null,"is_over_budget":false,"category_count":1}
```

A degraded fallback run instead reports `"status":"degraded"` with
`"fallback_active":true` - that pair, not the HTTP code, is the fallback
signal (REQ-OPS-011/012).

## Expected Behavior

The health endpoint answers `200` with the four documented fields
(`status`, `database`, `fallback_active`, `version`) served by
`backend/app/routers/health.py` through the `HealthResponse` schema;
`status` is `ok` exactly while no fallback is active. The auth pair issues
a JWT, the category and expense writes answer `201`, the list shows the
created row, and the dashboard summary aggregates it (`total` equals the
posted amount). If the primary database had timed out, `create_db_engine`
in `backend/app/database.py` would instead have logged a WARNING, built
the SQLite fallback engine, and latched `IS_FALLBACK` - the API keeps
serving, degraded, never erroring the whole dashboard (FR-DB-1).

## Verification

The comparison is mechanical: the health body equals the Expected Output
JSON above (field order included), every step code equals its measured
code, the expense list body contains the created note, and the dashboard
body carries the `total` key with the posted amount. The t41 ac3 gate
performs exactly this comparison against a backend it starts and tears
down itself; a mismatch on any step means the data path is broken at that
layer and the runbook section named in Recovery is the next stop.

## Recovery

When the health payload reports `fallback_active: true`, the primary
database is unreachable: check the `DATABASE_URL` wiring and the database
process, restore connectivity, then restart the API - the fallback flag is
startup-only by design, so recovery is confirmed when a fresh
`curl -fsS http://127.0.0.1:8137/api/v1/health` reports
`"fallback_active": false` again. Follow `ops/runbook.md` from there: the
numbered symptom sections (database connection, fallback, auth, data,
deployment) carry the cause/diagnosis/action clauses, including
`db.fallback_triggered` and `db.connection_restored` in the logging
vocabulary of `ops/logging.md`.

## Findings

The measured run reproduced the documented healthy baseline exactly: 6 of
6 smoke steps returned their expected codes, the health body matched the
schema in `ops/health-check.md` byte-for-byte, and the scratch database
plus server process were removed after the run with no residue in the
repository. No drift was found between the documented vocabulary
(`backend/app/routers/health.py`, `backend/app/schemas/health.py`) and the
served payload.

## Lessons

One timing fact is worth recording: with port 8001 held by a concurrent
Docker stack, this card's worked example deliberately runs on the pinned
8137 port instead of touching Docker - the diagnosis flow is endpoint
configuration, not code, and the same commands work against any host/port
pair, including the deployed URL once its live comparison is un-deferred
(see the `LIVE_DEPLOYMENT_STATE` row). The fallback never corrupts the
picture either: health stays truthful (`degraded`, not `ok`) while SQLite
carries the load, which is exactly what makes the runbook's first question
- "what does health say?" - the right one.

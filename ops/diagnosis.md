# Diagnosis Worked Example

The REQ-OPS-040..048 worked example for the Expense Tracker Dashboard: one
real scenario carried end to end - symptom, steps, expected output copied
from a REAL measured run, expected behavior, verification, recovery,
findings and lessons. The steps below were executed against the local
backend on `127.0.0.1:8137` (the verification endpoint pinned by the t41
gate; the deployed endpoint is
`https://expense-tracker-dashboard-1qtu.onrender.com` and its measured live
health reading - `200` with `{"status":"ok","database":"postgresql",
"fallback_active":false,"version":"1.0.0"}` - is carried as the
`VERIFIED_ROW LIVE_DEPLOYMENT_STATE` in
`docs/criteria/security_ops_verification.md`). When a step's output
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


The alert-driven reading of the same flow. On 2026-10-17 this scenario did
not open with a user report at all: the alert DBFallbackActive fired, and the
drill left measured evidence behind. The rule lives in
observability/alerts.yaml, the single source of truth for every alert name
and metric name in this milestone, and it fires on the declared gauge
db_fallback_active (`== 1` for 5m, severity critical). The user report, if it
arrives at all, is the second signal - the fired rule is the first, and the
captured evidence is what an operator reads instead of a retelling.

### Alert-driven extension (of the healthy baseline)

This extension keeps every step of the healthy baseline above and changes
only the entry point: the operator starts from the firing rule and from what
the drill measured, then re-uses the same probes to confirm the state with
their own eyes.

1. The rule and its names. The firing rule is DBFallbackActive, declared in
   observability/alerts.yaml; the gauge it reads, db_fallback_active, is
   emitted by backend/app/telemetry.py from the merged startup latch, and the
   scrape that evaluates the rule is configured in
   observability/prometheus.yml. The operator view over the same series is
   observability/dashboard.json. Nothing here restates a name from memory:
   the rule file is where the names live.
2. The measured evidence chain. The drill's record is
   incident-response/incidents/2026-10-17-db-fallback-01/ and the three
   measured artifacts inside it:
   incident-response/incidents/2026-10-17-db-fallback-01/evidence.json (the
   harness manifest and captured legs),
   incident-response/incidents/2026-10-17-db-fallback-01/response.json (the
   read-only responder pass) and
   incident-response/incidents/2026-10-17-db-fallback-01/resolution.md (the
   measured resolution record). The bundle was collected by
   incident-response/collect-evidence.sh. Point at those files; do not
   re-author their contents here.
3. What a responder actually looks at. First the health payload, because
   `"status": "degraded"` with `"fallback_active": true` is the fallback
   signal this document already pins. Then the four telemetry series the rule
   set is built on: the db_fallback_active gauge the alert reads, plus the
   expense_created_total, expense_create_failures_total and
   category_created_total counters. Then the target_info attributes
   (service_name, deployment_environment, service_version), which say which
   build the numbers came from. In the drill the gauge read 1.0 while health
   said degraded - two independent legs agreeing on one fact.
4. Recovery verification. Recovery is not "the complaint stopped"; it is the
   merged runbook's conjunction - status ok AND fallback_active false -
   measured by incident-response/runbooks/verify-recovery.sh against the
   pinned loopback endpoint. The drill's real run, marker line and exit code
   are quoted in the incident's resolution.md.
5. The disclosed limits. The drill's own metrics leg came back `unavailable`
   at zero bytes, and the incident's resolution.md names the measured reason
   and defers the fix to a follow-up card rather than calling it fixed; the
   direct root-exposition capture in that record is what proves the series
   while the gap stands. The rule file is likewise not yet mounted into the
   running Prometheus container (recorded as a follow-up in the t76 card), so
   rule evaluation inside that container is a documented follow-up, not a
   present fact.
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


The alert-driven counterpart of this section is the incident record, not a
second copy of the output: the degraded health body, the log tail, the gauge
value and the counter values captured during the drill are held verbatim in
incident-response/incidents/2026-10-17-db-fallback-01/evidence.json and
summarised with their timestamps in the resolution.md beside it.
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


The alert side of recovery is equally mechanical: DBFallbackActive fires on
the db_fallback_active gauge while the latch is engaged, so the rule clears
only once a restarted process serves with the latch released and the scrape
sees the gauge back at 0. The verification is the merged
incident-response/runbooks/verify-recovery.sh, which reads the same payload
this section already names and refuses anything but the loopback endpoint;
the drill's measured recovery run is in
incident-response/incidents/2026-10-17-db-fallback-01/resolution.md.
## Findings

The measured run reproduced the documented healthy baseline exactly: 6 of
6 smoke steps returned their expected codes, the health body matched the
schema in `ops/health-check.md` byte-for-byte, and the scratch database
plus server process were removed after the run with no residue in the
repository. No drift was found between the documented vocabulary
(`backend/app/routers/health.py`, `backend/app/schemas/health.py`) and the
served payload.


The alert-driven pass added one finding of its own: the two independent
surfaces agreed. The gauge the fired rule reads and the health payload
reported the same fact at the same moment, which is what makes the alert
trustworthy as an entry point rather than a second opinion.
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

The second lesson is a voice lesson: this document used to start from what an
operator suspected. Starting from the fired rule and the captured evidence is
faster and auditable, because the rule name, the metric name and the evidence
paths are all files in the repository - observability/alerts.yaml for the
names, the incident directory for the measurements - and a document that
points at them cannot drift away from them the way a retelling can.

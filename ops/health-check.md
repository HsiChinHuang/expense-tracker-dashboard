# Health Check Reference

The single operational signal for the Expense Tracker Dashboard:
`GET /api/v1/health`. Render gates every deploy on it, UptimeRobot probes it
every 60 seconds, and the runbook's symptom sections start from its payload.
The documented schema and values below are the ones shipped by
`backend/app/routers/health.py` and `backend/app/schemas/health.py` and
asserted by the merged health and fallback tests — this file quotes them, it
does not invent them.

## Endpoint

- Method and path: `GET /api/v1/health`
- Router: `backend/app/routers/health.py`
  (`APIRouter(prefix="/api/v1")`, `@router.get("/health")`)
- Response model: `HealthResponse` (`backend/app/schemas/health.py`)

## Authentication

No authentication. The endpoint is public by design (REQ-OPS-110): probes
(Render's `healthCheckPath`, UptimeRobot) hold no credentials, and the
payload carries no user data — only backend status. There is no auth
override, no token, no cookie; no authentication is required or accepted.

## Response

`200 OK` with the JSON body (example values):

```json
{
  "status": "ok",
  "database": "postgresql",
  "fallback_active": false,
  "version": "1.0.0"
}
```

If the database layer fails outside the fallback path, the request instead
fails into the `DATABASE_UNAVAILABLE` handler (`backend/app/core/errors.py`)
and the client receives `503` with `{"detail": "Database is currently
unavailable", "code": "DATABASE_UNAVAILABLE", "field": null}` — see runbook
section 3 in `ops/runbook.md`.

## Fields

| Field | Type | Values | Meaning |
| --- | --- | --- | --- |
| status | string | ok, degraded | ok = primary backend serving; degraded = the SQLite fallback is serving (computed as `status="degraded" if fallback_active else "ok"`). |
| database | string | postgresql, sqlite | Which backend answered the probe. |
| fallback_active | boolean | true, false | Whether the SQLite fallback is currently active. |
| version | string | semver | Application version (`APP_VERSION`, e.g. 1.0.0). |

## State Combinations

The four combinations of `status` x `database` x `fallback_active`
(REQ-OPS-013) — exactly four rows, one per state the probe can report:

| status | database | fallback_active | Meaning |
| --- | --- | --- | --- |
| ok | postgresql | false | Normal production: PostgreSQL primary is serving. |
| ok | sqlite | false | Local development: SQLite is the configured backend, not a fallback. |
| degraded | sqlite | true | Fallback active: PostgreSQL was lost and the SQLite file is serving; see runbook section 2 in `ops/runbook.md`. |
| degraded | postgresql | false | The impossible combination, documented so nobody "fixes" it: status is derived from fallback_active, so a healthy PostgreSQL can never report degraded. |

## When to Use

- Every deploy: Render refuses to promote a build whose
  `healthCheckPath: /api/v1/health` probe never turns green.
- Every 60 seconds: the UptimeRobot external probe.
- At any incident: the first operator command in runbook sections 1-3 of
  `ops/runbook.md`.

## How It Is Used

- Render: `healthCheckPath: /api/v1/health` in `render.yaml` gates deploy
  promotion and marks the service live.
- UptimeRobot: periodic external GET; a non-200 answer fires the email
  alert.
- Deploy verification: after a promote, the operator confirms the payload
  with `curl http://localhost:8000/api/v1/health` (the README's documented
  local port).
- Manual diagnosis: `curl http://localhost:8000/api/v1/health` locally, or
  the public URL in production; the `fallback_active` field is the one to
  watch (see `ops/logging.md` for the matching `db.fallback_triggered`
  event).

## What It Does Not Check

The probe is a cheap read; it deliberately does not test:

- database write access (a read-only connection passes)
- external services (there are none to call, and none are probed)
- disk space (the SQLite fallback file could be full and the probe still
  answers)
- memory or CPU headroom (see What Is Not Monitored in `ops/runbook.md`)

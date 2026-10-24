# Logging

Structured logging for the Expense Tracker Dashboard: one JSON object per
line on stdout, a fixed event vocabulary, and a hard never-logged boundary.
The format and the event names below are the ones the merged code emits
(`backend/app/services/auth_service.py`, `backend/app/auth/dependencies.py`,
`backend/app/database.py`, `backend/app/core/errors.py`) and the ones the
green tests assert.

## Format

Every log line is a single JSON object written to stdout:

```json
{"timestamp": "2026-02-14T09:12:33.482+00:00", "level": "INFO", "logger": "app.services.auth_service", "event": "auth.login", "extra_fields": {"user_id": "3fa8a0f2-6f3a-4d3e-9d1c-2b7f0f5c9a11"}, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"}
```

Fields: `timestamp` (ISO-8601 UTC), `level`, `logger` (the Python logger
name), `event` (the dotted event name from the table below), `extra_fields`
(the structured payload), `trace_id` (the 32-hex OpenTelemetry trace id of
the request that emitted the line, or `null` when no span is active - see
the Structured Field Reference), and `exception` (only on ERROR lines that
carry a stack summary).

## Levels

| Level | Use |
| --- | --- |
| DEBUG | Local diagnostics only; never relied on in production output. |
| INFO | Normal operational events: logins, registrations, CRUD writes, database connections. |
| WARNING | Recoverable anomalies a human should eventually look at: failed logins, token rejects, fallback activation. |
| ERROR | Request-failing faults: database errors mapped to 503, unhandled exceptions. |
| CRITICAL | Process-level failure that stops the service from serving at all. |

## Events

The frozen Chapter 13 §13.6 vocabulary — exactly seventeen events:

| event | level | fields |
| --- | --- | --- |
| auth.login | INFO | user_id |
| auth.login_failed | WARNING | reason |
| auth.register | INFO | user_id |
| budget.created | INFO | budget_id |
| budget.deleted | INFO | budget_id |
| budget.updated | INFO | budget_id |
| category.created | INFO | category_id |
| category.deleted | INFO | category_id |
| db.connected | INFO | backend |
| db.connection_restored | INFO | backend |
| db.error | ERROR | error_type |
| db.fallback_initialized | WARNING | backend |
| db.fallback_triggered | WARNING | reason |
| expense.created | INFO | expense_id |
| expense.deleted | INFO | expense_id |
| expense.updated | INFO | expense_id |
| unhandled.error | ERROR | error_type |

`auth.login_failed` and `db.error` may be emitted at ERROR when the failure
is not merely a rejected credential or a transient reconnect; the table
records the level of the routine occurrence.

The table above is the frozen vocabulary and stays at exactly seventeen
events: the trace work added a field, not an event. Every line in this
vocabulary additionally carries the `trace_id` field (it is a field on every
correlated line, never an event row of its own), so a reader who knows the
trace id of one request can pull every event line that request emitted -
see `docs/criteria/trace_correlation_verification.md` for the measured
two-request journey.

## Never Logged

The following never enter a log line, in any field (REQ-OPS-053):

- Passwords (in any form, including hashes).
- JWT tokens of any kind — access or refresh.
- Full request bodies or response bodies; only named identifiers are logged.
- Request bodies echoed on validation errors — field names only, never request bodies.
- Raw email addresses / Raw email text.
- Database connection strings (`$DATABASE_URL` and its components).
- Secrets: `JWT_SECRET`, API keys, and any configured credential.

## Log Destinations

- stdout — the only destination the application writes to (REQ-OPS-111).
- `docker compose logs` / `docker compose logs -f app` — local collection.
- The Render log viewer — platform collection of the container's stdout.

There are no log files and no log rotation to manage; the platform owns
retention (see Log Retention).

## Viewing Logs

Local:

```bash
docker compose logs -f app
```

Production: the Render dashboard's log viewer (same stdout stream).

### Filtering

The JSON shape makes every event greppable:

- Fallback activation: `docker compose logs -f app | grep '"event": "db.fallback_triggered"'`
- Failed logins: `docker compose logs -f app | grep '"event": "auth.login_failed"'`
- Database faults: `docker compose logs -f app | grep '"event": "db.error"'`
- Unhandled exceptions: `docker compose logs -f app | grep '"event": "unhandled.error"'`

## Log Retention

Session only — the platform keeps the recent stdout window and nothing more
on the free tier. There is no log archive, no search history, and no
retention SLA; download what you need from the Render log viewer before it
rolls off. This is a Free tier limitation, not a configured policy.

## Structured Field Reference

| Field | Type | Notes |
| --- | --- | --- |
| timestamp | string | ISO-8601 UTC with timezone. |
| level | string | One of the five levels above. |
| logger | string | Python logger name, e.g. `app.services.auth_service`. |
| event | string | Dotted event name from the Events table. |
| extra_fields | object | Structured payload; identifiers only, never secrets. |
| trace_id | string | 32-hex trace id of the correlated request; null when no span is active (backend/app/trace.py). |
| exception | string | Stack summary; present only when a fault is logged. |

The design properties are JSON-structured lines (machine-filterable without
a parser agent) written to stdout (container-native; the platform owns
collection).

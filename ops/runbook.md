# Operations Runbook

Operational reference for the Expense Tracker Dashboard (Render free tier,
Docker web service, PostgreSQL with the SQLite fallback). Symptom sections
first, then escalation, incident response, monitoring, backup/recovery and
rollback. Companion documents: `ops/health-check.md` (the health endpoint
reference), `ops/logging.md` (event vocabulary and log filtering), and
`ops/diagnosis.md` (worked diagnostic examples, added in the verification
card).

## Quick Reference

| Symptom | # |
| --- | --- |
| Cold start — the first request takes minutes | 1 |
| Degraded health — /api/v1/health reports degraded | 2 |
| 503 DATABASE_UNAVAILABLE on API calls | 3 |
| Login failures after a deploy | 4 |
| User data leak — one user sees another user's data | 5 |
| Deployment failure on Render | 6 |
| Tests fail in CI | 7 |

## 1. Cold Start — First Request Takes Minutes

### Symptom

The first request after an idle period takes many seconds (sometimes more
than a minute) and the visitor sees a spinner or a timeout instead of the
dashboard.

### Cause

Render spins the free web service down after 15 minutes without traffic
(documented under Platform Constraints); the container restart costs seconds
to minutes, and the free PostgreSQL instance may also be starting.

### Diagnosis

- Check the Render service log for a fresh container start at the request time.
- `curl http://localhost:8000/api/v1/health` locally, or the public
  `/api/v1/health` URL, and time the response.
- A cold container logs the normal startup sequence (migrations, then
  "Application startup complete") right before the slow request.

### Action

- Wait — the service is up once startup completes; no operator action is
  required for a routine cold start.
- Confirm the entry now returns quickly; UptimeRobot's probe itself warms the
  service every 60 seconds, so cold starts mostly hit the first visitor after
  a longer outage of the probe.
- If the service never becomes healthy, follow section 6 (Deployment Failure).

*Source: Chapter 13 §13.3.2; the 15-minute idle spin-down is a free-tier plan
property documented in Platform Constraints below.*

## 2. Degraded Health (fallback_active true)

### Symptom

`GET /api/v1/health` returns HTTP 200 with `"status": "degraded"`,
`"database": "sqlite"` and `"fallback_active": true`.

### Cause

The application could not reach PostgreSQL and switched to the SQLite
fallback file so reads and writes keep working; the fallback is a
single-instance, on-disk copy, so data written while degraded does not live
in the primary database.

### Diagnosis

- Read the health payload (see `ops/health-check.md` for the field meanings).
- Filter the logs for the `db.fallback_triggered` event (`ops/logging.md`
  documents the filter); the line names the reason.
- Check Render's database metrics and the PostgreSQL log for restarts or
  connection-limit exhaustion.

### Action

- Do not restart the app — the reconnect is automatic; the logs emit
  `db.connection_restored` when the primary backend is reachable again.
- Treat degraded as a data-divergence window: writes made to SQLite during
  the window are not replayed to PostgreSQL, so reconcile them manually if
  any user mutation happened while degraded.
- If degraded persists, restart the PostgreSQL instance from the Render
  dashboard and watch for `db.connection_restored`.

*Source: Chapter 13 §13.3.3; the reconnect-on-next-request behaviour is
asserted by the merged fallback tests.*

## 3. 503 DATABASE_UNAVAILABLE

### Symptom

API calls return HTTP 503 with body `{"detail": "Database is currently
unavailable", "code": "DATABASE_UNAVAILABLE", "field": null}`.

### Cause

An unexpected SQLAlchemy error escaped the request path and the exception
handler in `backend/app/core/errors.py` mapped it to 503 — typically the
primary database is unreachable and the SQLite fallback could not serve the
query either (for example a Postgres-only feature or a file-system problem).

### Diagnosis

- The handler logs an ERROR line with the error type only (the SQLAlchemy
  message is deliberately not echoed to the client); filter for `db.error`
  per `ops/logging.md`.
- `curl http://localhost:8000/api/v1/health` — if it answers, the fallback is
  alive and the failing query is the differentiator; if it also 503s, the
  process itself cannot reach any database.

### Action

- Restart the Render database, then the web service, from the dashboard.
- If 503s continue after both restarts, roll back the last deploy per the
  Deployment Rollback section (a migration or query change is the likely
  regression).
- Escalate per the Escalation section if the condition survives a rollback.

*Source: Chapter 13 §13.3.4; the 503 mapping is the merged handler in
`backend/app/core/errors.py`.*

## 4. Login Failures After Deploy (JWT_SECRET Mismatch)

### Symptom

Every login or refresh from existing clients fails immediately after a
deploy; new registrations work, and the log shows `auth.login_failed`
WARNING lines.

### Cause

`JWT_SECRET` is generated by Render (`generateValue: true` in
`render.yaml`), so a recreated service gets a new secret and every previously
issued token fails signature verification. Rotating the secret deliberately
has the same effect.

### Diagnosis

- Filter the logs for `auth.login_failed` (`ops/logging.md` documents the
  filter); a spike right after a deploy is the signature.
- Compare the deploy timestamp in the Render Deploys view with the first
  failure timestamp.

### Action

- Tell affected users to log in again — the old tokens are unrecoverable by
  design and re-login is the only client-side fix.
- To keep tokens across deploys, pin `JWT_SECRET` as a static secret in the
  Render dashboard instead of regenerating it.
- If logins fail for *fresh* credentials too, this is not the mismatch case:
  check the database health first (sections 2 and 3).

*Source: Chapter 13 §13.3.5.*

## 5. User Data Leak (Missing user_id Filter)

### Symptom

One user can see another user's expenses, budgets, or categories — through
the UI, the API, or an agent reply.

### Cause

A query lost its `user_id` scoping (a new endpoint or service function was
added without the filter), or the JWT issuer stopped binding the verified
`user_id` to the query layer.

### Diagnosis

- Reproduce with two accounts and confirm the cross-read.
- Inspect the endpoint or service for a missing `WHERE user_id = ...` clause
  before anything else.
- Check whether a recent deploy touched CRUD or auth code.

### Action

- Contain immediately: pause the affected endpoint (revert the offending
  deploy via the Deployment Rollback section) and revoke all sessions by
  rotating `JWT_SECRET` in the Render dashboard — every issued token becomes
  invalid, forcing re-login.
- Record the incident (who saw what, when); the Incident Response section is
  the playbook.
- Fix forward with the missing filter plus a regression test, then redeploy.

*Source: Chapter 13 §13.3.6.*

## 6. Deployment Failure (Build or Startup)

### Symptom

A Render deploy fails during the Docker build, or the service starts but
never passes its health check and Render rolls the deploy back / leaves it
stopped.

### Cause

Common causes: a dependency resolution failure in the image build, a
migration that errors on startup (the image CMD runs migrations before
serving), or an environment variable that exists locally but not in the
dashboard.

### Diagnosis

- Read the build log and the runtime log in the Render dashboard.
- Reproduce locally with `docker compose up --build` and read the same
  startup output.
- Run the migrations locally with `make migrate` to surface migration
  errors before touching Render.

### Action

- Fix the build/startup error and push again; Render redeploys on push.
- If user traffic is being served by the currently running build, prefer
  rolling back to the last good build (Deployment Rollback section) over
  fixing forward under pressure.

*Source: Chapter 13 §13.3.7.*

## 7. Tests Fail in CI

### Symptom

The GitHub Actions run for a push or pull request goes red (backend pytest,
ruff, mypy, frontend vitest/tsc/eslint, or the Playwright e2e job).

### Cause

A code change broke behaviour, a lint or typing gate, or the e2e stack;
occasionally the CI environment itself (dependency install, Docker build).

### Diagnosis

- Read the failing job log and reproduce locally with the same gates:
  `make test-backend`, `make test-frontend`, `make e2e` (the Makefile
  is the single command vocabulary).
- If it reproduces locally, it is the change; if not, re-run the job once to
  rule out infrastructure flake.

### Action

- Never merge with a red required check; fix the failure on the branch.
- If the failure is infrastructure, re-run the job and note the flake in the
  PR so it is not papered over.

*Source: Chapter 13 §13.3.8.*

## Escalation

1. Reproduce and scope the symptom using this runbook's Quick Reference and
   the matching numbered section.
2. Read the structured logs with the event filters documented in
   `ops/logging.md` (and the worked examples in `ops/diagnosis.md`).
3. Check the Render dashboard: service runtime log, deploy history, and the
   database metrics ("Render logs" live here, not in a separate collector).
4. Check the health endpoint per `ops/health-check.md` to separate app
   failures from database failures.
5. If the issue is unresolved after the section's Action steps, open a
   GitHub issue with the symptom, the log lines, and the health payload, and
   assign it to the project maintainer (the sole operator on this project).

## Incident Response

Breach DETECTION for this project is log- and health-based: the event
vocabulary in `ops/logging.md` (especially `auth.login_failed`, `db.error`,
`unhandled.error`) plus the periodic health probe is what surfaces an
incident; there is no IDS or WAF on the free tier (see What Is Not
Monitored).

Response steps:

1. Contain the blast window: revert the offending deploy or pause the
   affected endpoint (see Deployment Rollback).
2. Revoke all sessions by rotating `JWT_SECRET` in the Render dashboard —
   every issued token dies with the old secret and users re-authenticate.
3. Preserve evidence: download the relevant Render log lines and the health
   payload before restarting anything.
4. Fix forward with a regression test, redeploy, and confirm via
   `curl http://localhost:8000/api/v1/health` and the filtered logs.
5. Record the incident in the GitHub issue: detection time, containment
   time, data affected, and the rollback (if any) that was used.

## Monitoring

- Render dashboard — the primary operational view: uptime, runtime logs,
  deploy history, and the free PostgreSQL instance's connection metrics.
- UptimeRobot — external 60-second probe of the public health endpoint;
  alerts by email when the probe fails.
- The health endpoint itself — `GET /api/v1/health` is the single signal
  both tools consume; `ops/health-check.md` documents its fields and the
  four state combinations.

## Alerting

No pager exists on this project. UptimeRobot sends an email when the health
probe fails (and when it recovers); Render emails deploy failures. The
operator reads email — that is the entire alerting chain, and it is a known
limitation rather than an oversight (REQ-OPS-081 documents the boundary).

## What Is Not Monitored

The following are deliberately outside the MVP monitoring boundary:

- CPU utilisation — no metric collector on the free tier.
- Memory usage — the 512 MB ceiling is enforced by Render, not observed by us.
- Request latency percentiles — no APM or metrics pipeline.
- Error rate — ERROR log lines exist but nothing aggregates them.
- Connection pool — connection pool saturation is not exported or scraped.
- Disk usage of the SQLite fallback file — not watched.

## Future Monitoring

If the project ever leaves the free tier, the documented upgrade path is:

- Prometheus for metric collection (CPU, memory, latency, error rate) with
  Grafana dashboards on top.
- UptimeRobot alert channels beyond email (SMS/Slack) and multi-endpoint
  checks.
- Sentry for error tracking with release correlation.
- Alertmanager-style routing so alerts page someone instead of emailing.
- Log shipping (structured JSON off-platform) to replace session-only logs.
- Scheduled backups with restore drills, replacing the manual export
  discipline below.

## Backup and Recovery

**No automated backups are configured.** Scope: this is the documented
decision, not an omission (REQ-OPS-090/093, REQ-DB-121).

- Free tier limitation — Render's free PostgreSQL plan offers no automated
  backup or PITR window to configure.
- Cost — automated cross-region backups would mean a paid plan for a
  personal-scale app.
- Data volume — small, single-user, low-volume dataset: a manual dump
  finishes in seconds.
- Scope — the SQLite fallback file is a local file, so a file copy *is* its
  backup; nothing here justifies a backup service.

Manual export (run before any risky operation):

```bash
pg_dump $DATABASE_URL > backup.sql
sqlite3 fallback.db .dump > fallback_backup.sql
```

Restore:

```bash
psql $DATABASE_URL < backup.sql
sqlite3 fallback.db < fallback_backup.sql
```

The commands are the standard `pg_dump`/`psql`/`sqlite3` tools; `$DATABASE_URL`
is the Render connection string from the dashboard. Future backups (paid
tier) are listed under Future Monitoring.

## Deployment Rollback

Rollback is the Render dashboard, not a CLI:

1. Open the service's Deploys view in the Render dashboard.
2. Find the last successful deploy (green, before the incident).
3. Click Redeploy on that commit — Render rebuilds and promotes the previous
   build.

### Rollback triggers

Per Chapter 13 §13.11 and REQ-CICD-051, roll back when:

- a deploy ships a user-visible regression and the fix is not minutes away;
- the health endpoint goes red or degraded right after a deploy;
- 503 DATABASE_UNAVAILABLE appears only on the new build (section 3);
- login failures spike immediately after a deploy (section 4).

### Database rollback

Migrations are forward-only-not-rolled-back: `alembic downgrade` is not part
of the procedure. A rollback redeploys the previous *application* build;
the schema stays at the newer migration revision. New migrations are written
as forward-only-not-rolled-back changes (additive, backward-compatible with
the previous build) precisely so this asymmetry is safe.

### Limitations

- forward-only migrations mean a rollback cannot undo schema changes;
- no canary deploy exists on the free tier — every deploy is all-or-nothing;
- no blue-green deploy either — there is a brief interruption during
  promotion;
- Rollback takes minutes (rebuild time), not seconds;
- data written between the bad build and the rollback stays in the database.

## Platform Constraints

Documented so operators do not debug properties of the plan as if they were
bugs (REQ-ARCH-080; cross-checked against `render.yaml`):

- 512 MB RAM per service (`ram: 512` in the paid-plan sense; the free plan
  enforces the same ceiling) — memory-hungry requests fail, they do not
  swap.
- 0.1 CPU (`cpu: 0.1`) — one tenth of a core; slow builds and slow first
  queries are expected.
- 15 minutes idle spin-down — the service sleeps without traffic (section 1).
- `plan: free` for both the web service and the PostgreSQL instance, so the
  database may also be cold, and `healthCheckPath: /api/v1/health` gates
  every deploy.

## Operational Design Choices

| Choice | Alternative | Why |
| --- | --- | --- |
| Health endpoint is Public, no auth | Authenticated health | Probes (Render, UptimeRobot) hold no credentials; the payload carries no user data (REQ-OPS-110). |
| JSON structured logs to stdout | Text logs to files | Machine-filterable without a log agent; containers should not own files (REQ-OPS-111). |
| stdout as the only destination | File + platform shipper | Render collects stdout; a shipper is a paid-tier concern. |
| Monitoring = Render + UptimeRobot | Prometheus/Grafana now | Two free probes cover uptime and health; metrics are the documented future step. |
| Backups Manual only | Automated backup jobs | Free tier has no scheduler for it and the dataset is minutes to dump (see above). |
| Rollback = Render redeploy of previous build | Blue-green/canary | The free tier offers neither; redeploy of a known-good build is the primitive that exists. |
| SQLite fallback with degraded health | Hard-fail on DB loss | Reads and writes survive an instance restart; the divergence window is documented in section 2. |
| Migrations run in the container start command | External migration job | One image, one code path; a failed migration fails the deploy visibly. |

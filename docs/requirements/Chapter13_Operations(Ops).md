# Chapter 13: Operations (Ops)

## 13.1 Overview

This chapter covers how the application is operated after deployment.
It includes health checks, runbooks, diagnosis procedures, logging,
and deployment verification. It maps to Final Project Criterion 13
(operational diagnosis output) and Criterion 10 (deployment proof).

### 13.1.1 Ops Directory Layout

```
ops/
├── runbook.md
├── health-check.md
├── diagnosis.md
├── logging.md
└── deployment-health.md
```

### 13.1.2 Purpose of Each File

| File | Purpose |
|---|---|
| runbook.md | Common problems and how to diagnose them |
| health-check.md | Health endpoint reference |
| diagnosis.md | Worked example: database fallback |
| logging.md | Log format, levels, events |
| deployment-health.md | Post-deployment verification record |

## 13.2 Health Check Endpoint

### 13.2.1 Endpoint

```
GET /api/v1/health
```

No authentication required. Used by Render, CI/CD, and UptimeRobot.

### 13.2.2 Response Schema

```json
{
  "status": "ok",
  "database": "postgresql",
  "fallback_active": false,
  "version": "1.0.0"
}
```

### 13.2.3 Fields

| Field | Type | Values | Meaning |
|---|---|---|---|
| status | string | ok, degraded | degraded when fallback is active |
| database | string | postgresql, sqlite | Current database engine |
| fallback_active | boolean | true, false | Whether SQLite fallback is in use |
| version | string | semver | Application version |

### 13.2.4 State Combinations

| status | database | fallback_active | Meaning |
|---|---|---|---|
| ok | postgresql | false | Normal production state |
| ok | sqlite | false | Local development with SQLite |
| degraded | sqlite | true | Production fallback active |
| degraded | postgresql | false | Should not occur |

### 13.2.5 Usage

| Consumer | Purpose |
|---|---|
| Render | Health check path for the web service |
| CI/CD | Verify deployment succeeded |
| UptimeRobot | Keep service warm, detect downtime |
| Manual | Quick status check |

### 13.2.6 Render Health Check Configuration

In `render.yaml`:

```yaml
services:
  - type: web
    name: expense-tracker-dashboard
    healthCheckPath: /api/v1/health
```

Render pings this endpoint periodically. If it fails, Render marks the
service as unhealthy.

## 13.3 Runbook

**File**: `ops/runbook.md`

```markdown
# Operations Runbook

This runbook lists common problems and how to diagnose them.

## Quick Reference

| Symptom | Likely Cause | Section |
|---|---|---|
| First request slow | Cold start on free tier | 1 |
| Health shows degraded | PostgreSQL unreachable | 2 |
| All requests return 503 | Database error | 3 |
| Login fails for everyone | JWT_SECRET mismatch | 4 |
| Users see each other's data | Missing user_id filter | 5 |
| Deployment fails | Build or migration error | 6 |
| Tests fail in CI | Dependency or env mismatch | 7 |

## 1. Cold Start (Render Free Tier)

### Symptom
First request after idle takes 30-60 seconds.

### Cause
Render free tier sleeps the service after 15 minutes of inactivity.

### Diagnosis
Check Render logs for "Starting service" after the delay.

### Action
- Wait for the service to wake up.
- UptimeRobot pings every 10 minutes to reduce cold starts.
- This is expected behavior on the free tier.

## 2. Health Shows Degraded

### Symptom
`GET /api/v1/health` returns `status: degraded` and
`fallback_active: true`.

### Cause
PostgreSQL was unreachable at startup. The app fell back to SQLite.

### Diagnosis
1. Check `/api/v1/health` for `database: sqlite`.
2. Check Render dashboard for the PostgreSQL service status.
3. Check application logs for `db.fallback_triggered`.

### Action
1. If PostgreSQL is down, wait for Render to recover it.
2. Restart the web service to reconnect to PostgreSQL.
3. Verify `/api/v1/health` shows `database: postgresql`.
4. Note: data written during fallback is temporary.

## 3. All Requests Return 503

### Symptom
Most endpoints return 503 DATABASE_UNAVAILABLE.

### Cause
Database connection lost at runtime.

### Diagnosis
1. Check `/api/v1/health`.
2. Check application logs for `db.error`.
3. Check Render PostgreSQL status.

### Action
1. If the database is down, wait for recovery.
2. Restart the web service.
3. If the issue persists, check the DATABASE_URL environment variable.

## 4. Login Fails for Everyone

### Symptom
All login attempts return 401 INVALID_CREDENTIALS, even with
correct passwords.

### Cause
`JWT_SECRET` mismatch between deployments, or users were created
with a different secret.

### Diagnosis
1. Check Render environment variables for `JWT_SECRET`.
2. Check application logs for `auth.login_failed` spikes.
3. Verify the secret matches the one used at user creation.

### Action
1. If the secret changed, users must re-register or you must
   re-issue tokens.
2. Do not change `JWT_SECRET` casually; all existing tokens become
   invalid.

## 5. Users See Each Other's Data

### Symptom
A user reports seeing another user's expenses or budgets.

### Cause
Missing `user_id` filter in a query. This is a critical bug.

### Diagnosis
1. Check the affected endpoint's service method.
2. Verify every query filters by `user_id`.
3. Check the isolation tests.

### Action
1. Fix the query immediately.
2. Add a regression test in `test_isolation.py`.
3. Redeploy.
4. Verify with two accounts.

## 6. Deployment Fails

### Symptom
Render deployment fails or the service does not start.

### Cause
Build error, migration error, or environment variable missing.

### Diagnosis
1. Check Render build logs.
2. Check for missing environment variables.
3. Check Alembic migration output.

### Action
1. Fix the build error locally first.
2. Run `alembic upgrade head` locally to verify migrations.
3. Redeploy.
4. If the new version is broken, roll back to the previous deploy.

## 7. Tests Fail in CI

### Symptom
GitHub Actions CI fails on a pull request.

### Cause
Dependency mismatch, environment difference, or a real bug.

### Diagnosis
1. Check the CI log for the failing test.
2. Reproduce locally with the same command.
3. Check if the dependency lock file changed.

### Action
1. Fix the failing test or the code.
2. Update `uv.lock` or `package-lock.json` if dependencies changed.
3. Push the fix.

## Escalation

If a problem is not covered here:

1. Check `ops/diagnosis.md` for a worked example.
2. Check `ops/logging.md` for log format.
3. Check Render logs.
4. Check the GitHub issue tracker.
```

## 13.4 Health Check Reference

**File**: `ops/health-check.md`

```markdown
# Health Check Reference

## Endpoint

```
GET /api/v1/health
```

## Authentication

None. This endpoint is public.

## Response

```json
{
  "status": "ok",
  "database": "postgresql",
  "fallback_active": false,
  "version": "1.0.0"
}
```

## Fields

| Field | Values | Meaning |
|---|---|---|
| status | ok, degraded | ok when primary database is connected |
| database | postgresql, sqlite | Current database engine |
| fallback_active | true, false | Whether SQLite fallback is in use |
| version | semver | Application version |

## When to Use

| Situation | Expected Response |
|---|---|
| Normal production | status=ok, database=postgresql, fallback_active=false |
| Local development | status=ok, database=sqlite, fallback_active=false |
| Production with fallback | status=degraded, database=sqlite, fallback_active=true |
| Database down at startup | status=degraded, database=sqlite, fallback_active=true |

## How It Is Used

### Render

`render.yaml` sets `healthCheckPath: /api/v1/health`. Render pings
this endpoint and marks the service unhealthy if it fails.

### CI/CD

The deploy workflow calls this endpoint after deployment:

```bash
curl -f https://expense-tracker-dashboard.onrender.com/api/v1/health
```

If the response is not 200, the deploy is considered failed.

### UptimeRobot

UptimeRobot pings every 10 minutes to keep the service warm and to
detect downtime.

### Manual

```bash
curl https://expense-tracker-dashboard.onrender.com/api/v1/health
```

## What It Does Not Check

- Database write access (only read)
- External service availability
- Disk space
- Memory usage

For these, use Render metrics.
```

## 13.5 Operational Diagnosis Example

**File**: `ops/diagnosis.md`

This is the worked example required by Criterion 13.

```markdown
# Operational Diagnosis: Database Fallback

## Scenario

PostgreSQL becomes unreachable at application startup. The application
falls back to SQLite to keep serving requests.

## Why This Matters

On Render's free tier, the PostgreSQL database expires after 30 days.
Without fallback, the application would be completely unavailable.
With fallback, users can still use all features; data is just not
persisted across restarts.

## Steps to Reproduce

1. Start the full stack with PostgreSQL:
   ```bash
   docker compose up --build
   ```

2. Verify the app uses PostgreSQL:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Expected: `{"status":"ok","database":"postgresql","fallback_active":false}`

3. Stop the database:
   ```bash
   docker compose stop db
   ```

4. Restart the backend so it tries to connect at startup:
   ```bash
   docker compose restart app
   ```

5. Observe the logs:
   ```bash
   docker compose logs app
   ```

## Expected Log Output

```json
{"timestamp":"2026-10-15T12:34:56Z","level":"WARNING","event":"db.fallback_triggered","error":"connection refused"}
{"timestamp":"2026-10-15T12:34:57Z","level":"INFO","event":"db.fallback_initialized"}
```

## Expected Health Response

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "status": "degraded",
  "database": "sqlite",
  "fallback_active": true,
  "version": "1.0.0"
}
```

## Expected Behavior

| Feature | Behavior During Fallback |
|---|---|
| Register | Works |
| Login | Works |
| Create expense | Works |
| List expenses | Works |
| Set budget | Works |
| Dashboard | Works |
| Data persistence | Lost on restart |

## Verification

1. Register a new user:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","username":"testuser","password":"password123"}'
   ```
   Expected: 201

2. Login:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```
   Expected: 200 with access_token

3. Create an expense using the token.

4. List expenses. Expected: the created expense appears.

## Recovery

1. Restart the database:
   ```bash
   docker compose start db
   ```

2. Restart the backend so it reconnects to PostgreSQL:
   ```bash
   docker compose restart app
   ```

3. Verify:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Expected: `{"status":"ok","database":"postgresql","fallback_active":false}`

## Findings

| Observation | Result |
|---|---|
| Fallback triggered within | 5 seconds |
| User-facing errors during switch | None |
| CRUD endpoints during fallback | All functional |
| Dashboard during fallback | All charts render |
| Data written during fallback | Temporary (lost on restart) |
| Log clarity | Clear WARNING with reason |
| Health endpoint accuracy | Correctly reports degraded |

## Lessons

1. The fallback is a safety net, not a persistence solution.
2. The health endpoint must be checked before assuming production
   is healthy.
3. UptimeRobot would detect the change if it checks the `status`
   field.
4. A restart is required to switch back to PostgreSQL. This is a
   deliberate simplification.

## Related

- `ops/runbook.md` section 2
- `ops/health-check.md`
- `ops/logging.md` event `db.fallback_triggered`
```

## 13.6 Logging

**File**: `ops/logging.md`

```markdown
# Logging

## Format

Logs are JSON-structured for machine parsing.

```json
{
  "timestamp": "2026-10-15T12:34:56.789Z",
  "level": "INFO",
  "logger": "app.services.expense_service",
  "event": "expense.created",
  "extra_fields": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "expense_id": "660e8400-e29b-41d4-a716-446655440001",
    "amount": "125.50"
  }
}
```

## Levels

| Level | Used For |
|---|---|
| DEBUG | Development only; verbose detail |
| INFO | Normal operations |
| WARNING | Recoverable issues |
| ERROR | Failures requiring attention |
| CRITICAL | Not used in this project |

## Events

| Event | Level | Fields |
|---|---|---|
| auth.register | INFO | user_id |
| auth.login | INFO | user_id |
| auth.login_failed | WARNING | email_hash |
| expense.created | INFO | user_id, expense_id, amount |
| expense.updated | INFO | user_id, expense_id |
| expense.deleted | INFO | user_id, expense_id |
| budget.created | INFO | user_id, year_month |
| budget.updated | INFO | user_id, year_month |
| budget.deleted | INFO | user_id, year_month |
| category.created | INFO | user_id, category_id |
| category.deleted | INFO | user_id, category_id |
| db.connected | INFO | type |
| db.fallback_triggered | WARNING | error |
| db.fallback_initialized | INFO | - |
| db.connection_restored | INFO | - |
| db.error | ERROR | error |
| unhandled.error | ERROR | error, type |

## Never Logged

- Passwords (plain or hashed)
- JWT tokens
- Full request bodies
- Full response bodies
- Raw email addresses (use a hash)
- Database connection strings with credentials
- Secrets of any kind

## Log Destinations

| Environment | Destination |
|---|---|
| Local | stdout |
| Docker Compose | stdout (view with `docker compose logs`) |
| Render | Render log viewer |

## Viewing Logs

### Local

```bash
docker compose logs -f app
```

### Render

Render Dashboard → Service → Logs.

### Filtering

Render log viewer supports text search. Search for:

- `fallback_triggered` — database fallback occurred
- `auth.login_failed` — failed login attempts
- `db.error` — database errors
- `unhandled.error` — unexpected errors

## Log Retention

| Environment | Retention |
|---|---|
| Local | Session only |
| Render | Per Render free tier policy |

For long-term retention, logs would need to be exported to an
external service. This is out of scope.

## Structured Field Reference

| Field | Type | Description |
|---|---|---|
| timestamp | ISO 8601 UTC | When the event occurred |
| level | string | Log level |
| logger | string | Python module name |
| event | string | Event identifier |
| extra_fields | object | Event-specific fields |
| exception | string | Stack trace (only on errors) |
```

## 13.7 Deployment Health Record

**File**: `ops/deployment-health.md`

```markdown
# Deployment Health Record

This document records the state of the deployed application after
each significant deployment.

## Deployment 1: Initial Production

### Deployment Info

| Field | Value |
|---|---|
| Platform | Render (free tier) |
| URL | https://expense-tracker-dashboard.onrender.com |
| Date | 2026-10-15 |
| Version | 1.0.0 |
| Commit | abc1234 |

### Health Check

```bash
curl https://expense-tracker-dashboard.onrender.com/api/v1/health
```

```json
{
  "status": "ok",
  "database": "postgresql",
  "fallback_active": false,
  "version": "1.0.0"
}
```

### Smoke Test

| Step | Result |
|---|---|
| Register new user | PASS |
| Login | PASS |
| Add expense | PASS |
| Set budget | PASS |
| Dashboard renders KPI cards | PASS |
| Category pie chart renders | PASS |
| Monthly trend chart renders | PASS |
| Cumulative line chart renders | PASS |
| Weekly heatmap renders | PASS |
| Budget progress bar renders | PASS |
| Month switch updates charts | PASS |
| Recent transactions list | PASS |
| Logout | PASS |
| Re-login | PASS |

### Screenshots

- `screenshots/dashboard.png`
- `screenshots/expense-form.png`
- `screenshots/health-check.png`

### Cold Start

| Observation | Value |
|---|---|
| Cold start time | ~45 seconds |
| Warm response time | < 300 ms |
| UptimeRobot interval | 10 minutes |

### Database

| Field | Value |
|---|---|
| Engine | PostgreSQL 16 |
| Plan | Render free |
| Storage | 1 GB |
| Expiry | 30 days from creation |

### Notes

- Cold start is expected on the free tier.
- UptimeRobot keeps the service mostly warm.
- The database will expire on 2026-11-14. After that, the app will
  fall back to SQLite automatically.
- Peer reviewers can continue using the app after the database
  expires; data just will not persist.

## Deployment 2: After Database Expiry

### Deployment Info

| Field | Value |
|---|---|
| Date | 2026-11-15 |
| Reason | Render free PostgreSQL expired |
| Action | None; fallback activated automatically |

### Health Check

```json
{
  "status": "degraded",
  "database": "sqlite",
  "fallback_active": true,
  "version": "1.0.0"
}
```

### Smoke Test

All features work. Data is temporary.

### Notes

- This is the expected behavior.
- Users can still register, log in, and use all features.
- Data is lost on each restart.
- This state is acceptable for peer review.
```

## 13.8 Diagnosis Automation

The project does not include automated diagnosis scripts, but the
following commands are useful for manual diagnosis.

### 13.8.1 Check Service Status

```bash
curl -s https://expense-tracker-dashboard.onrender.com/api/v1/health | jq
```

### 13.8.2 Check Response Time

```bash
curl -w "%{time_total}s\n" -o /dev/null -s \
  https://expense-tracker-dashboard.onrender.com/api/v1/health
```

### 13.8.3 Check Database Connection

```bash
curl -s https://expense-tracker-dashboard.onrender.com/api/v1/health | jq '.database'
```

### 13.8.4 Check Fallback State

```bash
curl -s https://expense-tracker-dashboard.onrender.com/api/v1/health | jq '.fallback_active'
```

### 13.8.5 Check API Docs

```
https://expense-tracker-dashboard.onrender.com/docs
```

FastAPI's interactive docs are available in production. They provide
a live view of the OpenAPI spec.

## 13.9 Monitoring and Alerting

### 13.9.1 Monitoring

| Tool | What It Monitors |
|---|---|
| Render dashboard | Service status, logs, metrics |
| UptimeRobot | HTTP status, response time |
| Health endpoint | Database state, fallback state |

### 13.9.2 Alerting

| Alert | Trigger | Channel |
|---|---|---|
| Service down | UptimeRobot detects non-200 | Email |
| Fallback active | Manual check of `/health` | None (manual) |

### 13.9.3 What Is Not Monitored

| Metric | Reason |
|---|---|
| CPU usage | Render provides basic metrics |
| Memory usage | Render provides basic metrics |
| Request latency | Not instrumented in MVP |
| Error rate | Available in logs, not aggregated |
| Database connection pool | Not exposed |
| Disk usage | Not applicable (no persistent disk) |

### 13.9.4 Future Improvements

| Improvement | Priority |
|---|---|
| Prometheus metrics endpoint | Medium |
| Grafana dashboard | Medium |
| Alert on fallback activation | High |
| Alert on error rate spike | Medium |
| Structured log export | Low |
| Distributed tracing | Low |

## 13.10 Backup and Recovery

### 13.10.1 MVP Scope

- No automated backups
- PostgreSQL data is lost when Render free database expires
- SQLite fallback data is lost on container restart
- Manual export is documented but not automated

### 13.10.2 Manual Export

```bash
# PostgreSQL
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# SQLite
sqlite3 fallback.db .dump > backup-$(date +%Y%m%d).sql
```

### 13.10.3 Recovery

```bash
# PostgreSQL
psql $DATABASE_URL < backup-20261015.sql

# SQLite
sqlite3 fallback.db < backup-20261015.sql
```

### 13.10.4 Why No Automated Backups

| Reason | Explanation |
|---|---|
| Free tier limitation | Render free PostgreSQL has no backup feature |
| Scope | Demo project, not production |
| Data volume | Small, easily recreated |
| Cost | Automated backups require paid tier or external storage |

### 13.10.5 Future Improvements

| Improvement | Priority |
|---|---|
| Daily automated backup to S3 | High |
| Backup restoration test | High |
| Point-in-time recovery | Medium |
| Cross-region replication | Low |

## 13.11 Deployment Rollback

### 13.11.1 Rollback Procedure

If a deployment causes problems:

1. Go to Render Dashboard → Service → Deploys.
2. Find the previous successful deploy.
3. Click "Redeploy".

The service will restart with the previous version.

### 13.11.2 Rollback Triggers

| Trigger | Action |
|---|---|
| Health check fails after deploy | Rollback immediately |
| Smoke test fails | Rollback immediately |
| Users report broken feature | Assess, then rollback if needed |
| Fallback activated unexpectedly | Investigate, then decide |

### 13.11.3 Database Rollback

Database migrations are forward-only in this project. If a migration
causes problems:

1. Restore from a manual backup (if available).
2. Or, accept the fallback state and redeploy.

There is no automated migration rollback.

### 13.11.4 Rollback Limitations

| Limitation | Impact |
|---|---|
| No automated rollback | Manual step required |
| No database rollback | Data may be lost |
| No canary deploy | All users affected at once |
| No blue-green deploy | Downtime during rollback |

## 13.12 Operational Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Health endpoint | Public, no auth | Needed by Render and CI |
| Health fields | status, database, fallback_active, version | Covers key states |
| Fallback trigger | Startup only | Predictable, no runtime switching |
| Fallback reporting | In health endpoint | Visible to reviewers |
| Logging | JSON structured | Parseable, searchable |
| Log destination | stdout | Standard for containers |
| Monitoring | Render + UptimeRobot | Free, sufficient for demo |
| Alerting | UptimeRobot email | Simple, free |
| Backup | Manual only | Free tier limitation |
| Rollback | Render redeploy | Simple, effective |
| Diagnosis | Documented example | Reproducible by reviewer |
| Deployment record | Markdown file | Evidence for Criterion 10 |
| Ops documentation | 5 files | Covers runbook, health, diagnosis, logging, deployment |
```

---

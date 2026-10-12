# Deployment Health Record

## Purpose

This file is the deployment record required by REQ-OPS-060/061/062: the
initial deployment record, the post-expiry (fallback-then-recovery) record,
and the smoke-test evidence behind each. Every field is either a measured
repo-side value (a real commit, the health output measured on the local
backend on 2026-10-12, the smoke results recorded in
`docs/criteria/security_ops_verification.md`) or an explicit pointer to the
`LIVE_DEPLOYMENT_STATE` DEFERRED row in that same criteria document.
Nothing here is invented: where the harness could not measure the live
Render deployment (the configured URL answered `404` from this host,
measured), the field points at the deferral row and its operator live-check
instead of asserting a value.

## Initial Deployment

- **Date**: 2026-10-10 (the deploy-pipeline commit date, measured from git).
- **Commit**: `d60803a` - `feat(t26): CI/CD pipeline definitions - ci/e2e/deploy workflows, render.yaml, Makefile test targets, README deploy notice` (the commit that introduced `render.yaml` with `healthCheckPath: /api/v1/health` and `.github/workflows/deploy.yml`).
- **Health response**: `{"status":"ok","database":"sqlite","fallback_active":false,"version":"0.1.0"}` - the health body measured against the same build on the local backend on 2026-10-12 (see `ops/diagnosis.md`, Expected Output). The live Render comparison is DEFERRED: see the `LIVE_DEPLOYMENT_STATE` row in `docs/criteria/security_ops_verification.md` (the configured URL returns 404 from this harness, measured).
- **Smoke**: REQ-CICD-061 sequence executed against the local backend on 2026-10-12 - open the app URL, register a user, log in, add an expense, set a budget, verify the five dashboard charts, switch month: register `201`, login `200`, category `201`, expense `201`, expense list `200` (created row present), dashboard summary `200` (`total` equals the posted amount). The budget/month/chart legs of the front-end smoke are covered by the merged front-end suite (187 tests, 0 failed) and the e2e workflow; the live-deployment run of the same sequence is DEFERRED with the same `LIVE_DEPLOYMENT_STATE` row.
- **Notes**: Deploy path is `render.yaml` + `.github/workflows/deploy.yml` (workflow_run gated, REQ-CICD-041); the container runs `alembic upgrade head` before uvicorn serves (measured in `Dockerfile`); no security-scan job exists in CI by REQ-CICD-073, re-attested by the `WORKFLOW_SET_ROWS` row.

## Post-Expiry Deployment

The post-expiry record documents the fallback-then-recovery cycle the
deployment is expected to survive (Render's free-tier idle expiry,
REQ-OPS-062): the primary database or cold-start path becomes unavailable,
`create_db_engine` falls back to SQLite and health reports `degraded`, then
a restart after connectivity returns restores the primary backend.

- **Date**: 2026-10-12 (the date the fallback and recovery flow was re-measured for this milestone by the merged t25/t28 evidence and this card's executed diagnosis run).
- **Commit**: `56bb093` - `fix(t46): unblock E2E startup - runtime uv-cache ownership and compose CORS JSON` (the current tip of the deployable tree at record time, measured from git).
- **Health response**: healthy baseline `{"status":"ok","database":"sqlite","fallback_active":false,"version":"0.1.0"}` measured on the local backend; the post-expiry signature is the same body with `"status":"degraded"` and `"fallback_active":true`, and recovery is confirmed only when a fresh probe reports `false` again (`ops/diagnosis.md`, Recovery). The live post-expiry observation on Render is DEFERRED (`LIVE_DEPLOYMENT_STATE`).
- **Smoke**: the same REQ-CICD-061 sequence (open URL, register, add expense, set budget, verify the five charts, switch month) re-executed on 2026-10-12 with the same results as the initial record - all six API steps returned their expected codes and the dashboard `total` matched the posted expense; the front-end register/budget/charts/month legs stay green in the merged suite.
- **Notes**: The fallback is startup-only by design (REQ-BE-133): the flag is latched once by `create_db_engine` in `backend/app/database.py`, so expiry recovery requires a restart, and the runbook's database sections carry the operator clauses. The 60-second UptimeRobot probe (`ops/health-check.md`) is the external witness for this cycle; its live readings remain covered by the t28 `LIVE_COLD_START` deferral.

## Accepted Deviation: render.yaml versus the Chapter 14 §14.4.2 template

The stored `render.yaml` diverges from the Chapter 14 §14.4.2 blueprint
template. This is an **accepted deviation**, recorded here rather than
fixed in the blueprint: the stored positive blueprint gate
(`docs/state/merge_test_index.json` tests[134], issue t26) validates the
current file, and adding template keys the gate does not require would
risk that green gate for no measured benefit (t49 card, ac5; render.yaml
is NOT modified by this card - it stays byte-identical at the digest
pinned in ac6). Divergent keys, named one by one:

| §14.4.2 template key | Template value | Committed `render.yaml` | Why the deviation is accepted |
|---|---|---|---|
| `region` (service and database) | `oregon` | absent (Render default region) | Region is a deployment-time choice, not a contract; the gate does not require it and the free-plan resource set is unchanged. |
| `autoDeploy` | `false` | absent (platform default) | Releases are gated by `.github/workflows/deploy.yml` (workflow_run), so the platform default does not change the shipped path. |
| `databaseName` | `expense` | absent (Render generates it) | The app consumes only the `connectionString` property; no code or migration depends on the database name. |
| `user` (database) | `expense` | absent (Render generates it) | Same reason: credentials come from the generated connection string, never from the blueprint. |
| `CORS_ORIGINS` | JSON array `'["https://expense-tracker-dashboard.onrender.com"]'` | bare URL string | The merged settings parser accepts the plain URL (the t46 compose fix already aligned the container path with this shape); the JSON-array literal would double-encode against the merged parser. |

The database name in the committed file is `expense-tracker-db` (the
template's `expense-db`); it is referenced consistently by the service's
`fromDatabase` pointer, so renaming it would only break the blueprint.

## Live comparison (DEFERRED pointer)

The operator command that closes the deferred live fields is recorded in
`docs/criteria/security_ops_verification.md`:

```text
DEFERRED LIVE_DEPLOYMENT_STATE - curl the configured Render health URL and
compare the answer to the two records above.
```

Until that comparison runs, the two records above stand on measured
repo-side evidence only, and no line in this file claims a live Render
observation.

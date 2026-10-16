# Resolution: 2026-10-17-db-fallback-01 (measured DB-fallback drill)

Incident `2026-10-17-db-fallback-01`. This is the resolution record of a
MEASURED drill: the merged t80 evidence harness was executed, drill traffic
was generated against the degraded server, the Prometheus exposition was
scraped directly, and recovery was verified by the merged t82 runbook. Every
claim below carries the measured output that supports it. Nothing here was
authored ahead of the run: the drill ran on this machine against
`http://127.0.0.1:8137/api/v1`, and the timestamps are the real UTC times the
commands produced.

## 1. Evidence bundle (harness run)

The drill was executed with the merged harness, from the repository root,
after preparing the pinned venv (`python3 scripts/venv_path.py --root backend
--create`):

```
bash incident-response/collect-evidence.sh 2026-10-17-db-fallback-01 \
  --base-url http://127.0.0.1:8137/api/v1 --simulate-fallback --print-manifest
```

The harness's printed manifest (verbatim stdout; the same manifest is embedded
in `evidence.json` alongside the four captured legs):

```json
{
  "incident_id": "2026-10-17-db-fallback-01",
  "collected_at": "2026-10-16T18:19:18Z",
  "endpoint": "http://127.0.0.1:8137/api/v1",
  "legs": {
    "health": {"status": "ok", "file": "health.json", "bytes": 82},
    "log_tail": {"status": "ok", "file": "log_tail.txt", "bytes": 628},
    "metrics": {"status": "unavailable", "file": "metrics.txt", "bytes": 0},
    "version": {"status": "ok", "file": "version.txt", "bytes": 41}
  },
  "tree_hash": "30980c4a7e4f13423caab81a51d7279e9522026e4f7362f940b3117afb963cd6",
  "script_sha256": "7fee18e7e307294e4816a20ccbd34bc50e1427999f5b313f9f9853e4d8af26aa"
}
```

The metrics leg is the collector's own disclosed gap: status `unavailable`,
zero bytes. Section 5 proves, with measured probes, exactly why.

## 2. Timeline (real UTC, monotonic, anchored on the evidence)

| Time (UTC) | Event |
|---|---|
| 2026-10-16T18:19:18Z | Harness collected the evidence bundle (`collected_at`, identical in `evidence.json`) |
| 2026-10-16T18:19:47Z | First drill-traffic attempt against the harness server: curl exit code 7 (connection refused) - the harness had already torn its server down at bundle end |
| 2026-10-16T18:20:07Z | Builder-owned degraded server (same dead DSN as `--simulate-fallback`) confirmed degraded on 8137; first register attempt answered 422 (missing `username` field), corrected |
| 2026-10-16T18:20:16Z | Drill traffic on the degraded server: register 201, login 200, category 201 |
| 2026-10-16T18:20:24Z | expense 201 created; second expense 404 `CATEGORY_NOT_FOUND` (domain failure path exercised) |
| 2026-10-16T18:20:27Z | Direct scrape of the ROOT `/metrics` exposition: HTTP 200, 61366 bytes, business counters materialized by the traffic |
| 2026-10-16T18:20:33Z | Four-URL probe pair measured (the metrics-gap proof, section 5) |
| 2026-10-16T18:20:52Z | Recovery verified: merged runbook exited 0 with its verification marker (verbatim in section 6) |
| 2026-10-16T18:23:25Z | `response.json` authored by the read-only responder pass; validator exit 0 (ACCEPT) |

## 3. The degraded state, as captured

Health capture from the bundle (verbatim `health.json`, also embedded in
`evidence.json`):

```json
{"status":"degraded","database":"sqlite","fallback_active":true,"version":"0.1.0"}
```

Log tail from the bundle (verbatim `log_tail.txt`) - the merged
`backend/app/database.py` startup probe logging the fallback engagement, and
the 404 that section 5 is about:

```text
INFO:     Started server process [2036246]
INFO:     Waiting for application startup.
PostgreSQL unreachable for postgresql+psycopg://expense:change-me-locally@127.0.0.1:55432/expense_tracker; falling back to sqlite:///./fallback.db (REQ-BE-130)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8137 (Press CTRL+C to quit)
INFO:     127.0.0.1:59114 - "GET /api/v1/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59116 - "GET /api/v1/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59130 - "GET /api/v1/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59138 - "GET /api/v1/metrics HTTP/1.1" 404 Not Found
```

The version leg captured `86fbe454adfb132dfb31221bba5f54d1d364b62a`, the
commit the drill ran on. The `change-me-locally` fragment in the DSN is the
harness's own pinned dead-target placeholder, not a credential.

## 4. Drill traffic against the degraded server, and the direct exposition capture

The harness tears its server down when the bundle completes, so the first
traffic attempt (18:19:47 UTC) measured curl exit code 7 against a closed
port. The builder then started its own degraded server on the same pinned
port with the same dead target, and generated the traffic before scraping:

```
DATABASE_URL=postgresql+psycopg://expense:change-me-locally@127.0.0.1:55432/expense_tracker \
  python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8137
```

The server logged the same fallback engagement warning as the harness run.
Measured traffic (bodies abridged to the fields that matter; the login
response carried an access token, redacted here and never written to any
file in this bundle):

```text
POST /api/v1/auth/register   -> HTTP 201  (username drill-t84; created_at 2026-10-16T18:20:17)
POST /api/v1/auth/login      -> HTTP 200  (token redacted)
POST /api/v1/categories      -> HTTP 201  (id e6d5b96d-ea9d-41c7-9611-3dc188f3668f)
POST /api/v1/expenses        -> HTTP 201  (id 97c83dc2-a2fe-48ba-8906-acc659da93f3, amount 12.34)
POST /api/v1/expenses        -> HTTP 404  {"detail":"Category not found","code":"CATEGORY_NOT_FOUND","field":"category_id"}
```

Two successful creations and one domain-rejected creation, which is exactly
what the exposition below shows the business counters reading.

Direct scrape of the ROOT exposition (18:20:27 UTC, `curl -s
http://127.0.0.1:8137/metrics`, HTTP 200, 61366 bytes total). Verbatim
excerpt - the HELP/TYPE lines and samples as the process served them, with an
annotation line marking the elision:

```text
# HELP target_info Target metadata
# TYPE target_info gauge
target_info{deployment_environment="development",service_instance_id="1d32e443-7168-4b97-b309-fb0bf70d18ea",service_name="expense-tracker-api",service_version="1.0.0",telemetry_sdk_language="python",telemetry_sdk_name="opentelemetry",telemetry_sdk_version="1.45.1"} 1.0
[... unrelated process/HTTP histogram series elided ...]
# HELP category_created_total Custom categories that reached persistence.
# TYPE category_created_total counter
category_created_total{otel_scope_name="t79.telemetry.business",otel_scope_schema_url="",otel_scope_version=""} 1.0
# HELP expense_created_total Expense creations that reached persistence.
# TYPE expense_created_total counter
expense_created_total{otel_scope_name="t79.telemetry.business",otel_scope_schema_url="",otel_scope_version=""} 1.0
# HELP expense_create_failures_total Expense creations rejected by a domain error.
# TYPE expense_create_failures_total counter
expense_create_failures_total{otel_scope_name="t79.telemetry.business",otel_scope_schema_url="",otel_scope_version=""} 1.0
# HELP db_fallback_active 1 while the SQLite fallback latch is engaged.
# TYPE db_fallback_active gauge
db_fallback_active{otel_scope_name="t79.telemetry.business",otel_scope_schema_url="",otel_scope_version=""} 1.0
```

The three t79 business counters materialized only after the traffic above
(OTel counters appear on first add), the `db_fallback_active` gauge reads 1
while the health payload says `fallback_active true` - the two evidence legs
agree on the same fact - and `target_info` carries the three t78 resource
attributes (`service_name`, `deployment_environment`, `service_version`).
The scrape carried no other `*_total`/`*_active` business series.

## 5. The metrics-leg gap: measured probes, and the name it deserves

The harness metrics leg is `unavailable` at zero bytes. The measured reason:
the collector fetches `BASE_URL` + `/metrics`, i.e.
`/api/v1/metrics`, but the exposition is mounted at the ROOT `/metrics`.
Health is the mirror image. Probe pair, measured 18:20:33 UTC against the
degraded server (curl exit statuses included; 0 means the request completed
and the HTTP status is the answer):

```text
PROBE http://127.0.0.1:8137/api/v1/metrics -> HTTP=404 curl_rc=0
PROBE http://127.0.0.1:8137/metrics       -> HTTP=200 curl_rc=0
PROBE http://127.0.0.1:8137/api/v1/health -> HTTP=200 curl_rc=0
PROBE http://127.0.0.1:8137/health        -> HTTP=404 curl_rc=0
```

`/api/v1/metrics` answers 404 while `/metrics` answers 200, and
`/api/v1/health` answers 200 while `/health` answers 404. This is the t80
harness metrics-URL assembly defect: the collector appends `/metrics` to the
versioned API base instead of the server root, so its metrics leg can only
ever record a zero-byte gap on this application. It is a harness defect, not
a missing endpoint, and per this card's own rule a drill-revealed defect
becomes a NEW card, never an opportunistic patch here: it is deferred to a
follow-up card raised by the orchestrator (no number is claimed in this
record). The direct root-`/metrics` capture in section 4 is why that capture
is mandatory rather than optional: it is where the t78/t79 series are proven
measured while the collector's own leg cannot reach them.

## 6. Recovery verification (merged runbook, real output)

Recovery in this environment means: restart the API with `DATABASE_URL`
unset so the process binds the configured default engine again. In plain
words: the recovered engine is the configured default engine (the SQLite
file the merged configuration pins as the default), NOT PostgreSQL. No
PostgreSQL server exists on this host, so the drill could not and did not
claim a PostgreSQL recovery. The condition the merged runbook verifies is
the conjunction `status` ok AND `fallback_active` false - not either field
alone.

The degraded server was killed (only the builder's own process), the server
was restarted with `DATABASE_URL` unset, and the merged runbook was run
against the pinned loopback endpoint. Its real output and exit status:

```text
$ bash incident-response/runbooks/verify-recovery.sh
RECOVERY_VERIFIED: status ok AND fallback_active false (database=sqlite version=0.1.0)
exit code: 0
```

(The runbook script was executed from an LF-normalised working copy because
this Windows worktree smudges shell scripts to CRLF; the bytes of the
merged `incident-response/runbooks/verify-recovery.sh` are unchanged and
byte-checked by ac5.)

The recovered health payload, captured directly from the same process:

```json
{"status":"ok","database":"sqlite","fallback_active":false,"version":"0.1.0"}
```

And the recovered process's own gauge, scraped from the root exposition at
the same moment - the counter series reset because this is a new process,
while the gauge tells the truth about the new process state:

```text
target_info{deployment_environment="development",service_instance_id="76ee05f8-9525-4216-9dbf-76d6a17ea094",service_name="expense-tracker-api",service_version="1.0.0",telemetry_sdk_language="python",telemetry_sdk_name="opentelemetry",telemetry_sdk_version="1.45.1"} 1.0
db_fallback_active{otel_scope_name="t79.telemetry.business",otel_scope_schema_url="",otel_scope_version=""} 0.0
```

The measured before/after pair: `{"status":"degraded",...,"fallback_active":true,...}`
in section 3 against `{"status":"ok",...,"fallback_active":false,...}` here,
with the runbook marker above as the verification of the conjunction.

## 7. Response pass boundary

`response.json` is the read-only AI on-call answer over the bundle's five
evidence files, validated by the merged t81 validator (exit 0, ACCEPT). It
records only policy-allowed actions and its `recovery_verified` is the
literal `false`: recovery is established by the runbook output in section 6,
never by the responder pass.

## 8. Raw capture disposition and cleanup

The raw `evidence/` capture directory the harness wrote (five files under
`incidents/2026-10-17-db-fallback-01/evidence/`) is t80 runtime output and is
NOT committed: this card adds exactly three files. The raw bundle was moved
to `scratch/raw-evidence/` (untracked working room) while `evidence.json` was
built programmatically from it, and the scratch directory - including the raw
capture, the server logs, the PID files and the LF working copies - is
removed after the fences are replayed, so the raw capture leaves no trace in
the repository delta.

Cleanup actually performed: only the two server processes the builder started
were killed (verified by port probe returning connection-refused afterwards);
no other process was touched. The drill's runtime databases -
`fallback.db` (the fallback store both degraded servers wrote, CWD-relative
as `backend/app/database.py` pins) and any `dev.db` - were removed from every
path the merged database module writes to, because `.gitignore` line 181
(`*.db`) makes a stray database invisible to any git-derived purity check.

## 9. Disclosures and residual risks

- The version leg captured `86fbe454adfb132dfb31221bba5f54d1d364b62a`, the
  commit at drill time; if the branch moves before the fences replay, the
  ac1 probe explicitly tolerates the token differing from current HEAD
  (disclosed in its own evidence line).
- The t80 harness metrics-URL assembly defect is open and deferred to a
  follow-up card (section 5); until it lands, every future bundle for this
  endpoint will carry the same zero-byte metrics gap shape (ii).
- The recovery proves the fallback LATCH released and the default engine is
  serving; it does not prove PostgreSQL reachability, which this host does
  not provide. A PostgreSQL-backed recovery drill needs an environment that
  actually runs PostgreSQL.
- The drill user and its rows live only in the deleted `fallback.db` file; no
  credential, token value, or `.env` content appears in any file in this
  bundle.

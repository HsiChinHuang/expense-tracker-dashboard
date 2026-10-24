# Trace-ID correlation journey record (t122, measured)

This is the measured record behind the Observability 2/2 claim: two
401-producing requests, each emitting EXACTLY ONE correlated app log line
whose `trace_id` equals the id of the span the request exported. The ids
below are PRINTED FROM THE PASSING TEST RUN of
`backend/tests/integration/test_trace_correlation_api.py` (pytest `-s`,
3 passed), never invented. Reproduce in 30 seconds from the repository root:

```
cd backend && uv run pytest tests/integration/test_trace_correlation_api.py -q -s
```

The run prints one `TRACE_JOURNEY_MEASURED` line per request; the ids are
copied from that output into the rows below.

## Two correlated request/trace pairs (stack=testclient)

The driven pair is the two unauthenticated list endpoints (GET
/api/v1/expenses and GET /api/v1/categories without an Authorization
header): each produces a 401, each emits exactly one correlated app log
line (the auth WARNING), and neither needs a database fixture.

TRACE_JOURNEY PASS journey=expenses-list-401 trace_id=5f4dd6e9c3684ae8077f04d04e1bba42 log_lines=1 stack=testclient PASS
TRACE_JOURNEY PASS journey=categories-list-401 trace_id=0a72f92a96a60ab9696b3b3e47c13ae8 log_lines=1 stack=testclient PASS

## Per-line evidence table

| trace_id | request | log line (one per request - the measured truth) |
|---|---|---|
| 5f4dd6e9c3684ae8077f04d04e1bba42 | GET /api/v1/expenses (no header, 401) | the auth WARNING whose formatted line ends `"trace_id": "5f4dd6e9c3684ae8077f04d04e1bba42"`, equal to the exported SERVER span id |
| 0a72f92a96a60ab9696b3b3e47c13ae8 | GET /api/v1/categories (no header, 401) | the auth WARNING whose formatted line ends `"trace_id": "0a72f92a96a60ab9696b3b3e47c13ae8"`, equal to the exported SERVER span id and distinct from the id above |

A third, out-of-request probe span (created outside any request by the
test's control 4) carried a third distinct id, proving the id is per-request
and not process-scoped.

## Quoted frozen-vocabulary log line (real run, isolated SQLite database)

The 401 WARNING above is not in the frozen seventeen-event vocabulary, so
the quoted line here was measured from a REAL `POST /api/v1/auth/login`
against a throwaway database file (`auth.login` is vocabulary row 1):

{"timestamp": "2026-10-24T14:33:34.644567+00:00", "level": "INFO", "logger": "app.services.auth_service", "event": "auth.login", "extra_fields": {"email_id": "97ca79153e992748"}, "trace_id": "5de68935552602243f65c27afe2e694a"}

The same run's access-formatted line read
`auth.login "trace_id": "5de68935552602243f65c27afe2e694a"`.

## Honesty boundary (staged-config-only)

Everything measured above runs in-process under TestClient. The local
compose stack (`observability/compose.yaml`: otel-collector, Tempo, Loki -
enabled for this milestone) is staged local configuration only: render.yaml
deploys none of this stack (no collector, Tempo or Loki process is hosted),
and the earlier hosted probe of /metrics returned the SPA fallback document,
not an exposition. The trace_id on the log line is real in the hosted
process's stdout because backend/app/trace.py is merged deployed code; the
collector/Tempo/Loki destination is local-only.

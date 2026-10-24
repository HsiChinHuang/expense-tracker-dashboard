# Scoring-map verification record - telemetry dimensions

Milestone: phase_20_readme_scoring_map. Card: t115 (platform issue 121).
This file is t115's entire deliverable and the evidence record the README Part 2
table cites. Every claim was re-measured by the builder against the shipped tree
at build time (main 73b00f6, 2026-10-23); the card's fences re-measure each one,
so a path or count that moves without this record moving turns a fence RED
rather than leaving a stale claim standing.

Honesty rule (binding on every line): a claim is allowed only if a reader can
check it within 30 seconds at the named First entry point. This cluster is where
the rule bites hardest: the project carries a LOT of real observability machinery
and two specific, discoverable absences (no shared trace ID; the on-call agent
diagnoses while a human fixes). Both halves are stated, and each shortfall below
the maximum carries a Gap line. Because this cluster grades the RUN system, every
artifact below is classified as deployed-running or staged-config-only: the
hosted deployment (render.yaml) runs exactly one web service and one database -
no Prometheus, Alertmanager, Grafana, collector, Tempo or Loki process runs
anywhere hosted, and no hosted process executes the on-call responder.

## Observability

- Claim: 2/2
- Reason: metrics, structured logs and the collection/storage/UI stack are real and locatable in 30 seconds - four declared metric names with a single source of truth in observability/alerts.yaml, a /metrics exposition served by backend/app/telemetry.py (deployed-running code, but mounted only when ENVIRONMENT is development and only to a loopback peer: a 2026-10-23 probe of the hosted /metrics returned the SPA fallback document, not an exposition, because render.yaml sets ENVIRONMENT to production), one-JSON-object-per-line logs with a frozen seventeen-event vocabulary and an explicit never-log list naming JWT_SECRET and API keys (ops/logging.md, emitted by the merged code and therefore running in the hosted process's stdout), and a Prometheus + Alertmanager + Grafana stack whose dashboard.json visualises every declared name. The rubric's second clause - metrics, traces and logs sharing a trace ID - is now MET BY MEASUREMENT: backend/app/trace.py opens one W3C-traceparent SERVER span per request and a handler-level correlation filter stamps the 32-hex trace_id onto every correlated app log line (measured: exactly one correlated line per request, the log id equal to the exported span id, ids distinct across requests, a third distinct id from an out-of-request span - docs/criteria/trace_correlation_verification.md), and the OTel collector / Tempo / Loki block in observability/compose.yaml is ENABLED as three active services with collector.yaml mounted, so the trace has a named local destination. Classification stays honest: the collector/Tempo/Loki destination is staged local configuration only - render.yaml deploys none of it - while the trace_id on the log line is real hosted-process output because backend/app/trace.py is merged deployed code.
- First entry point: `observability/README.md`
- Evidence: `observability/alerts.yaml`, `observability/prometheus.yml`, `observability/dashboard.json`, `backend/app/telemetry.py`, `backend/app/trace.py`, `ops/logging.md`, `observability/compose.yaml`, `observability/collector.yaml`, `docs/criteria/trace_correlation_verification.md`, `render.yaml`
- Deep dive: `docs/criteria/security_ops_verification.md`
- Gap: closed 2026-10-24 - the absence this line recorded (no shared trace_id, commented collector/Tempo/Loki block) is replaced by the measured trace_id correlation in backend/app/trace.py (journey record: docs/criteria/trace_correlation_verification.md) and the enabled local collector/Tempo/Loki stack; the hosted classification is unchanged: render.yaml still deploys none of that stack.

## Alerting on User Impact

- Claim: 1/1
- Reason: observability/alerts.yaml (the single metric-name authority) declares two alert rules that fire on user impact, not on CPU - HighExpenseCreationFailures ratios failed expense creates against created expenses, and DBFallbackActive fires while the database fallback latch is engaged (degraded data quality users can feel); the alert path was drilled, not just configured: the measured incident record incident-response/incidents/2026-10-17-db-fallback-01 carries five intact artifacts from alert firing to resolution. Classification, stated plainly: the rules are real files and the drill is measured (docs/criteria/security_ops_verification.md line PHASE13_ALERT_RULES rules=2 PASS), but the evaluator is the local compose stack, not the hosted deployment - observability/prometheus.yml's own header records that the local compose mounts the scrape config but not alerts.yaml, so no Prometheus process on this project evaluates these rules continuously anywhere.
- First entry point: `observability/alerts.yaml`
- Evidence: `observability/alerts.yaml`, `incident-response/incidents/2026-10-17-db-fallback-01`, `docs/criteria/security_ops_verification.md`
- Deep dive: `docs/criteria/security_ops_verification.md`

## On-Call Agent

- Claim: 2/2
- Reason: the agent wakes on an alert and produces a machine-checkable diagnosis - incident-response/responder-task.md is its task contract, collect-evidence.sh builds the evidence bundle, response.schema.json plus validate_response.py pin and validate the answer shape, and the 2026-10-17 drill record proves the loop ran end to end; the rubric's second point is now earned the narrow honest way: t123 merged the third policy class safe_local_remediation (the restart_local_compose_app id, local-compose-only) and t124's documented rehearsal - recorded in docs/criteria/oncall_drill_verification.md - makes that one remediation RECORDABLE in actions_taken while restart_production, database_mutation and merge stay denied. Classification: the responder is a task contract executed on demand, not a running service - render.yaml deploys no agent process, and the drill directory is the measured execution rather than a continuously operating automation.
- First entry point: `incident-response/responder-task.md`
- Evidence: `incident-response/autonomy-policy.yaml`, `incident-response/collect-evidence.sh`, `incident-response/response.schema.json`, `incident-response/validate_response.py`, `incident-response/runbooks/rollback.sh`, `incident-response/runbooks/verify-recovery.sh`, `ops/diagnosis.md`
- Deep dive: `ops/diagnosis.md`
- Gap: the fix half is a DOCUMENTED rehearsal, not a live remediation - this environment's docker daemon is unreachable (measured: index legs 188/192 RED-at-tip), so docs/criteria/oncall_drill_verification.md pins mode documented-rehearsal, live_container_operation false and recovery_verified false; responder-task.md keeps the boundary ("You diagnose; a human operates") and autonomy-policy.yaml keeps default_decision deny over restart_production, database_mutation and merge, so the recorded action is one narrow local id a human operated, never an instruction to act.

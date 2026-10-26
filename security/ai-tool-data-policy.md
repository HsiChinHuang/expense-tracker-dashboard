# AI Tool Data Policy

Data policy for every AI tool that touches the Expense Tracker Dashboard:
the extension pack's skills, hooks, MCP server, and read-only subagents
(docs/agent-extension-pack.md), plus the coding agents that build the tree.
The governing premise is the local-only data statement (REQ-AI-133): all
expense, budget, and audit data is local to the deployment — an AI tool is
never a data controller here, only a constrained processor acting through
the public HTTP API with its user's JWT.

## Tool Inventory

| Tool | Class | Data access path |
| --- | --- | --- |
| add-expense skill | agent procedure | Public HTTP API with a real JWT, after the validate-amount hook |
| budget-check skill | read-only agent procedure | Public HTTP API with a real JWT; reports and warns, never writes |
| monthly-report skill | read-only agent procedure | Public HTTP API with a real JWT; aggregates own-user rows only |
| MCP server (4 tools) | thin API wrapper | Public HTTP API only — never the database, never a DB credential |
| custom-agent subagents (2) | read-only agents | Public HTTP API with a real JWT |
| Coding agents (build pipeline) | repository tooling | Source tree only; runtime data is out of bounds |

## Data Classification

| Category | Examples | Handling rule |
| --- | --- | --- |
| Personal expense data | amounts, dates, notes, category ids | Own-user scope only; ownership hook plus API filter bind every read/write |
| Budget data | year_month, amounts | Read-only to reporting skills; writes need the user's own JWT |
| Audit records | audit_logs rows (action, entity_type, old_value, new_value, ip_address) | Written by the service layer in-transaction; no AI tool writes them directly |
| Secrets | JWT_SECRET, DATABASE_URL | Never present to any AI tool; Render-sourced platform secrets (REQ-SEC-120) |
| Public repository text | source, docs, CI config | Readable; untrusted-instruction handling per the agent threat model |

## Data Flow

User or agent request -> hooks (validate-amount / validate-ownership) ->
public HTTP API over JWT-authenticated routes -> schema, service, and
database layers (ownership filter, same-transaction audit) -> response.
There is one data path: every agent read or write goes through the public
HTTP API with a real JWT; the MCP server is not the database and never
touches it.
No AI tool stores, caches, or forwards expense data outside the
deployment; nothing crosses the local boundary (REQ-AI-133).

## Permitted and Forbidden Uses

Permitted, acting for the authenticated owner:

- Read and write the owner's own expenses and budgets through the API.
- Produce budget-usage and monthly-report views from own-user rows.
- Read repository text for build, review, and scan purposes.

Forbidden outright:

- It is forbidden — never permitted under any prompt — for an AI tool to
  read another user's rows, attempt horizontal access, or bypass the
  ownership hook and API filter by any other channel.
- No AI tool may ever receive, store, log, or transmit a secret: JWT
  material, JWT_SECRET, database URLs, or Render secret values stay out of
  every prompt, file, and log line (REQ-SEC-120/121 hygiene; the gitleaks
  gate measures the tree at zero findings).
- No tool may write audit rows directly or mutate data outside the
  in-transaction service path.

## Compliance Notes

Compliance posture (REQ-SEC-103): the policy is a documentation control
reviewed at every phase gate; the composite no-drift gate re-checks that
the policy's agent statements still agree with the shipped extension pack
(JWT, read-only, public HTTP API). Data-subject actions (export, delete)
are satisfied by the own-user scoping of the API itself — a user's data is
exactly the rows their JWT can reach, deletable through their own session.

## Review Requirements

- Any change to the extension pack (new skill, hook, MCP tool, or subagent)
  requires a policy review in the same PR, recorded in
  `security/pr-audit.md`.
- The data-category table above and the inventory must be re-measured
  against the shipped pack counts whenever docs/agent-extension-pack.md
  changes.
- Dependency and scan findings that touch the data path (auth libraries,
  HTTP clients) are dispositioned in the Accepted Findings register of
  `security/agent-security-notes.md` before release.

## Incident Response

If a policy breach is suspected (data seen outside its owner's scope, a
secret in a prompt or the tree, an agent acting beyond its user's JWT):

1. Stop the affected agent/skill path (remove the JWT or the pack entry).
2. Rotate the exposed material — JWT_SECRET rotation invalidates sessions.
3. Follow the incident-response section of `ops/runbook.md` (the t39
   runbook): user-data-leak runbook entry 5, then escalation.
4. Verify blast radius from the `audit_logs` trail and record the
   post-incident note under `docs/log/`.

## Recorded Limitation: Distributed Tracing (t87 accepted-findings refresh)

Distributed tracing is NOT implemented for this milestone. Like the t86
self-reference boundary this policy already records, this disclosure is
documentation-only: it names a measurement gap and grants no new data
access — no secret, no personal data, and no expense row crosses the local
boundary because of it. The observability stack implements two of three
telemetry signals: metrics and logs are implemented, distributed tracing is
NOT. The OTel exporter stays disabled and the otel-collector / Loki / Tempo
block in `observability/compose.yaml` stays commented out on purpose (the
collector image is not published for this milestone), so no span exists for
any tool — scanner, agent, or auditor — to measure, trace, or disposition.
The t86 sweep therefore scanned metrics, logs, and the tree, and honestly
could not measure traces; the gap is recorded as limitation row 13 of the
Accepted Limitations table in `security/agent-security-notes.md`, matches the
same commented-block statement in `observability/README.md` and
`observability/collector.yaml`, and is closed only by a dedicated tracing
card that publishes the collector, uncommented compose block, and wired
exporter — after which spans can be measured and this row dropped.

## Disclosure refresh (t143 / #148) - supersedes the stale t87 sentences above; appended 2026-10-26

The t87 "Recorded Limitation: Distributed Tracing" section above states that the OTel
exporter "stays disabled" and that the otel-collector / Loki / Tempo block in
`observability/compose.yaml` "stays commented out on purpose". Both sentences are STALE
and are SUPERSEDED here rather than edited in place: the t87 stored gate keeps this
record ADD-ONLY against its pinned BASE, so an appended superseding paragraph is the
truthful instrument. The measured current state (re-read from the live tree at the t143
groom base): `observability/compose.yaml` defines otel-collector, loki and tempo as LIVE
services (realized by t122), `observability/collector.yaml` carries a LIVE traces
pipeline, and `backend/app/trace.py` installs the tracer and opens one SERVER span per
request. The residual gap this record still discloses is measurement, not definition:
the production install attaches no span processor, the locked environment ships no OTLP
exporter, and no CI or E2E job boots the observability compose stack, so no span is
exported to the collector and distributed traces are not measured, queried, or
dispositioned by any sweep. Like the t86 self-reference boundary this policy already
records and the t87 disclosure this paragraph supersedes, this refresh is
documentation-only: it names a measurement gap and grants no new data access - no
secret, no personal data, and no expense row crosses the local boundary because of it.

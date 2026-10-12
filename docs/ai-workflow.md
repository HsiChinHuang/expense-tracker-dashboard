# AI Workflow (docs/ai-workflow.md)

The honest record of how this repository was built with AI assistance:
which tools ran, what the workflow was, which real sessions shipped
real merges, which AI outputs were corrected, and which review and
data-policy rules made that safe. Every requirement cited below is
defined in `docs/requirements.md`; this file is the Verification
target of REQ-DOC-023 (the thirteen sections below), REQ-AI-110..113
(session records), REQ-AI-120..122 (correction log), REQ-AI-130..132
(data policy and review), REQ-AI-140..143 (tooling choices) and
REQ-SEC-072 (scan timing).

This document deliberately LINKS rather than duplicates the documents
other cards own (REQ-DOC-061): the pipeline lifecycle prose lives in
`docs/process.md`, the extension-pack specification lives in
`docs/agent-extension-pack.md` and `docs/permissions.md`, and the
tool data policy lives in `security/ai-tool-data-policy.md`.

## Tools

Two choices, both stated for the record under REQ-AI-140:

- **Agent and model**: `pi-agent` running `qwen3.8-27b`, locally. The
  reasons are the three in the requirement: local execution (nothing
  leaves the machine - see Data policy), zero per-call cost, and
  controllability of the context the model sees.
- **Supporting toolchain actually used in the sessions below**: the
  repo's own `make` targets (`make test`, `make security`, ...), the
  backend `uv` environment, the frontend `npm`/`vitest`/`tsc`
  toolchain, and the four scan tools named in Scan timing.

## Workflow

The full lifecycle (issue -> groom -> build -> verify -> merge ->
close, with the retry and amendment rules) is owned by
`docs/process.md` - read it there; it is not restated here
(REQ-DOC-061 link-not-duplicate). What this file records instead is
how the workflow *felt in practice*: every Session record below names
the phase it was executed in, and the Correction log below records
what went wrong at each phase.

## Context engineering

What the agent is given to read is a designed artifact, not an
afterthought:

- `AGENTS.md` is the tool-agnostic context root (REQ-AI-141): hard
  rules, role skills, and pointers, written so any agent tool can
  consume it unchanged.
- Role skills under `skills/` (builder, definer, verifier,
  orchestrator) carry the per-role procedure; the agent loads only
  its own role's skill.
- Issue cards under `docs/issues/` are the whole contract for a build
  - pinned verification commands included - so the agent never has to
  guess what "done" means.
- Machine state (`docs/state/issue_map.json`,
  `docs/state/merge_history.json`, `docs/state/merge_test_index.json`)
  is readable but orchestrator-owned; agents cite it and never edit
  it (see the Correction log entry on index pins).

## Roles

The three working roles match the course Part 1 split (REQ-AI-141):
PM (backlog, priorities), Software Engineer (build), QA (verify). The
role->owner mapping and escalation path are in `docs/process.md` and
`docs/ownership.md`; this file only records the AI-specific rule: an
agent may only ever act inside one role's allowed file set, and a
builder may never approve its own work (see Review).

## Orchestration

Stated against this repo as shipped (REQ-AI-142): the main `pi-agent`
session is the orchestrator; GitHub Issues is the backlog (every
`docs/issues/tN.md` has a platform issue number recorded in
`docs/state/issue_map.json`); execution is sequential for the MVP -
one issue at a time through build -> verify -> merge, which is why
the merge history is a linear story an auditor can follow. Subagent
worktrees exist (this file was drafted in one), but they never merge
themselves; only the orchestrator moves bytes onto main.

## Example prompts

Three prompts, quoted in spirit from the real sessions above (they
are examples here; the evidence records are the Session records,
which cite real merges):

1. "Implement the AC in docs/issues/t15.md exactly; run the pinned
   commands; do not modify the card." (implementation prompt shape)
2. "The verifier FAILED your branch on the pagination bound; read the
   FAIL handoff, fix only the failure, keep the delta pure."
   (repair prompt shape)
3. "Groom docs/issues/t44.md: which pinned index entries does the
   Makefile repair touch, and is an amendment needed?" (scoping
   prompt shape - the answer was the Option A-ter class of decision).

## Session records

REQ-AI-110: these records exist as evidence that AI tools were used
**and reviewed**. REQ-AI-111: each record carries date, tool, prompt,
agent output, human review, and commit. REQ-AI-112: the set covers
grooming, implementing, and re-verification phases. REQ-AI-113: the
`area=` tags span the phase vocabulary. Every `issue=tN` is a key of
`docs/state/issue_map.json` and every Commit sha is that issue's
recorded merge sha in `docs/state/merge_history.json` - the ac2
command machine-verifies exactly that, so nothing below is invented.

### SESSION 2026-10-07 | area=spec | issue=t0

- **Date:** 2026-10-07
- **Tool:** pi-agent (qwen3.8-27b) + orchestrator worktree
- **Prompt:** "Create the repo skeleton and the requirement tree the
  whole pipeline will hang off; nothing may reference code that does
  not exist yet."
- **Agent output:** the initial skeleton commit - docs tree,
  requirements, and the first merge_test_index entries.
- **Human review:** PM role checked the skeleton against the course
  chapters before merge; the merge was recorded, not self-approved.
- **Commit:** 1753fd07205d61318253fa1e20877ae4e1d2535a

### SESSION 2026-10-08 | area=auth | issue=t9

- **Date:** 2026-10-08
- **Tool:** pi-agent builder role (frontend worktree)
- **Prompt:** "Wire the frontend to the auth endpoints per
  docs/issues/t9.md; AC commands are pinned, run them verbatim."
- **Agent output:** login/register wiring with session handling;
  builder branch pushed for independent verification.
- **Human review:** verifier role re-executed the pinned commands at
  the branch tip before the merge decision.
- **Commit:** 1a89838

### SESSION 2026-10-08 | area=crud | issue=t15

- **Date:** 2026-10-08
- **Tool:** pi-agent builder role (backend worktree)
- **Prompt:** "Implement expense CRUD per the card; money is exact,
  users are isolated - if in doubt write tests, not prose."
- **Agent output:** CRUD endpoints plus the TESTS-ONLY isolation and
  money-precision round (13 nodes, zero production changes); index
  grew 77 -> 82.
- **Human review:** verifier adjudicated the AMOUNT_MAX ratification
  and the zero-baseline-amendment claim before merge.
- **Commit:** 32bc15c22

### SESSION 2026-10-09 | area=dashboard | issue=t19

- **Date:** 2026-10-09
- **Tool:** pi-agent builder role (backend service layer)
- **Prompt:** "Add dashboard aggregation; aggregation lives in the
  service, the router stays thin."
- **Agent output:** `dashboard_service.py` aggregation with the thin
  router pattern; backend suite at 230 green at merge.
- **Human review:** verifier ran the full cumulative index (100/100)
  and the ac6 end-to-end leg before merge.
- **Commit:** 5d0165d

### SESSION 2026-10-12 | area=security | issue=t36

- **Date:** 2026-10-12
- **Tool:** pi-agent builder role (security ops worktree)
- **Prompt:** "Land the five scan targets in the Makefile and the
  scan-report discipline; results are committed artifacts, never CI
  steps."
- **Agent output:** the `security-*` Makefile targets and report
  layout behind the Scan timing section below; 457 tests green at
  verify.
- **Human review:** verifier re-proved the gitleaks negative control
  independently before PASS.
- **Commit:** 7d5c328

### SESSION 2026-10-12 | area=testing | issue=t44

- **Date:** 2026-10-12
- **Tool:** pi-agent builder role (Makefile-only delta)
- **Prompt:** "Repair the semgrep recipe so the scan is repeatable
  headless; the delta is the Makefile line and nothing else."
- **Agent output:** the corrected `security-semgrep` recipe (see the
  Correction log entry for the `--metrics off` flag story).
- **Human review:** verifier executed the stored contract entry
  unamended on merged main before closing.
- **Commit:** a64a3a2be

### SESSION 2026-10-13 | area=deployment | issue=t49

- **Date:** 2026-10-13
- **Tool:** pi-agent builder role (root reviewer docs)
- **Prompt:** "Land the root reviewer docs and the README criteria
  map; README moves to its pinned digest and the runbook typo fix is
  in scope."
- **Agent output:** CLAUDE.md, product-spec.md, README criteria map +
  evidence checklist, and the deployment-deviation record; README
  landed at the pin-1 digest this card carries unchanged.
- **Human review:** verifier re-attested the README digest and the
  full MAIN floor set at the branch tip.
- **Commit:** 5e04b61

## Correction log

REQ-AI-120 format (date, issue, AI output, correction, lesson), plus
the REQ-AI-122 document-update linkage: every entry names the document
the correction updated. `docs/requirements.md` is the requirement
source every entry below was checked against, and the process/role
documents are what a correction has to update or the next session
repeats it (REQ-DOC-062). The six REQ-AI-121 example lesson classes
(pagination, Decimal, isolation, aggregation, heatmap week start,
referential integrity) each appear once, anchored to the card that
established the rule and to code that is still greppable in the merged
tree today. Where a lesson came from a review ruling rather than a
build failure, the entry cites the card line that records it -
nothing below is invented.

### CORRECTION 2026-10-08

- **Date:** 2026-10-08
- **Issue:** t15
- **AI output:** an expense-list implementation whose pagination
  envelope and out-of-range behaviour were left to the agent's
  judgement; the first pass treated `page_size` as a display detail
  rather than a validated contract.
- **Correction:** the bounds were pinned into the contract and the
  code - `page >= 1`, `1 <= page_size <= 100`, the frozen
  `{items,total,page,page_size}` envelope, and 422 for out-of-range
  values (REQ-API-040..044; the W16 inclusive-bounds matrix in
  `docs/issues/closed/t15.md`; visible today as the
  `Query(ge=1, le=100)` bound in `backend/app/routers/expenses.py`).
- **Lesson:** pagination bounds are an acceptance criterion, not
  polish - a free parameter the agent may default is a bug waiting to
  ship (REQ-AI-121 pagination class).
- **Document updated:** docs/requirements.md (REQ-API-040..044 bounds
  wording) and the pinned-contract block of `docs/task-template.md`.

### CORRECTION 2026-10-08

- **Date:** 2026-10-08
- **Issue:** t14
- **AI output:** budget arithmetic that reached for ordinary Python
  numbers, with amounts rendered as JSON floats.
- **Correction:** amounts are `decimal.Decimal` end-to-end and
  `quantize(Decimal("0.01"))`-normalised, transmitted as 2-dp
  **strings**, never as JSON numbers; "no float may appear in a
  service function or schema" is written into the card (REQ-DB-090/091,
  REQ-SEC-050; `docs/issues/closed/t14.md`; visible today in
  `backend/app/services/budget_service.py`).
- **Lesson:** never float money - the float default is the failure,
  not the test case that catches it (REQ-AI-121 Decimal class).
- **Document updated:** docs/requirements.md (REQ-DB-090/091,
  REQ-SEC-050) and the money-typing rule in the SWE role document
  `docs/team/software-engineer.md`.

### CORRECTION 2026-10-08

- **Date:** 2026-10-08
- **Issue:** t13
- **AI output:** models whose foreign keys declared no delete
  behaviour, so removing a user or a category would raise referential
  integrity errors at runtime instead of acting deliberately.
- **Correction:** delete semantics declared in the schema itself -
  `ondelete="CASCADE"` on the user foreign keys and
  `ondelete="RESTRICT"` where removal must be blocked, each proven at
  the database level rather than asserted (REQ-DB-030/032;
  `docs/issues/closed/t13.md`; visible today in
  `backend/app/models/budget.py` and `backend/app/models/expense.py`).
- **Lesson:** referential integrity is declared, not described - an
  undeleted parent row is a data-integrity bug the tests will not see
  until someone deletes something (REQ-AI-121 referential-integrity
  class).
- **Document updated:** docs/requirements.md (REQ-DB-032 FK wording)
  and the migration checklist in `docs/process.md`.

### CORRECTION 2026-10-09

- **Date:** 2026-10-09
- **Issue:** t15
- **AI output:** cross-user isolation treated as an implication of
  `WHERE user_id = ...` code review rather than as behaviour under
  test, so a green suite proved nothing about the boundary.
- **Correction:** isolation became its own test contract -
  `backend/tests/integration/test_isolation.py`, named in the t15 card
  (REQ-SEC-030/031: cross-user access returns 404, never 403/500, no
  existence leak) - under the card's W16 tests-only defect policy.
- **Lesson:** a security boundary without a dedicated node is an
  assumption, not a test (REQ-AI-121 isolation class).
- **Document updated:** the QA role document
  `docs/team/qa-engineer.md` and the test-evidence expectations in
  `docs/process.md`.

### CORRECTION 2026-10-09

- **Date:** 2026-10-09
- **Issue:** t19
- **AI output:** dashboard arithmetic written inside the router, which
  would have duplicated the aggregation rule across every future
  consumer.
- **Correction:** aggregation lives in the service and the router
  stays thin - the plan ruling quoted in `docs/issues/closed/t19.md`
  (visible today in `backend/app/services/dashboard_service.py`); the
  same card records the review correction that a blanket
  `! grep "float("` gate is unsatisfiable and was rejected in favour
  of behavioural checks.
- **Lesson:** aggregation belongs in the service, and a verification
  gate must be satisfiable to mean anything (REQ-AI-121 aggregation
  class).
- **Document updated:** the aggregation-location ruling recorded in
  `docs/process.md` and the role split in
  `docs/team/software-engineer.md`.

### CORRECTION 2026-10-09

- **Date:** 2026-10-09
- **Issue:** t20
- **AI output:** a weekly heatmap keyed on the chart library's
  Sunday-start week, which silently shifts every bucket by one day
  against the product definition.
- **Correction:** the week boundary became explicit data rather than a
  library default - the frozen wire shape carries `week_start` with
  exactly 7 days per week and "the heatmap weeks carry seven
  Monday-start days" is pinned in `docs/issues/closed/t20.md` (and
  structurally re-checked by the 52-row rule in
  `docs/issues/closed/t23.md`; visible today in
  `frontend/src/components/charts/weekly_heatmap.tsx`).
- **Lesson:** calendar semantics are product decisions; the agent must
  read the design contract, never inherit a library default
  (REQ-AI-121 heatmap week-start class).
- **Document updated:** the chart contract later consolidated into
  `docs/design-system.md` and the design rules in
  `docs/team/software-engineer.md`.

### CORRECTION 2026-10-10

- **Date:** 2026-10-10
- **Issue:** t28
- **AI output:** a verification attestation whose generated line
  embedded a fresh random token (`ATTEST_PHANTOM_TOKEN ... PASS`) on
  every run.
- **Correction:** the token made the attestation non-byte-stable, so it
  could not be pinned or diffed; the generator was fixed to emit
  deterministic content (negative-control record in
  `docs/issues/closed/t28.md`).
- **Lesson:** a verification artifact that changes between runs cannot
  be evidence - determinism is a correctness property of the check
  itself.
- **Document updated:** the verification rules in `docs/process.md`
  and the byte-stability convention this correction log follows.

### CORRECTION 2026-10-12

- **Date:** 2026-10-12
- **Issue:** t43
- **AI output:** a psycopg driver + fallback repair in which **every**
  shape collided with a byte-frozen merge_test_index entry: index
  tests[139] (t27, 0-based + issue_id convention) froze `backend/app`
  at an old digest, so the probe edit turned the stored gate RED -
  while the driver-only alternative turned four merged t25 entries RED
  and left the REQ-BE-130 fallback broken.
- **Correction:** the **Option A-ter** amendment: the orchestrator
  narrows the frozen entry at merge time (precedent t21 W2/W3, t36
  entry 6), with **both directions measured before** the amendment -
  WAL seq 558 (blocker raised), 559 and 580 (ruling and executed
  amendment) in `docs/log/2026_10_07.md` record the whole exchange.
- **Lesson:** stored index pins are living contracts, and a
  card-vs-pin conflict is resolved by measurement plus a recorded
  ruling - never by silently editing the pin or silently dropping the
  fix (the pin-amendment precedent this card follows).
- **Document updated:** the amendment rules in `docs/process.md` and
  the index-entry convention every later card cites.

### CORRECTION 2026-10-12

- **Date:** 2026-10-12
- **Issue:** t44
- **AI output:** a `security-semgrep` recipe that hung in headless
  runs because semgrep's metrics prompt never received an answer.
- **Correction:** the recipe runs `--metrics off` (WAL seq 550 FAIL for
  the uncorrected scan, seq 577 MERGE_OK for the repair in
  `docs/log/2026_10_07.md`; the `security-semgrep` target in the
  Makefile is the repaired line).
- **Lesson:** a scan recipe is only documented when it is repeatable
  headless - an interactive prompt is a hang in CI clothing.
- **Document updated:** the Makefile scan recipe itself and the
  Scan timing section below.

## Skills

Three skills ship in the pack (REQ-AI-143), one directory per skill
under `agent-capabilities/`: add-expense, budget-check,
monthly-report. The specification, trigger rules and hook coverage -
including the two hooks (`agent-hooks/validate-amount.py`,
`agent-hooks/validate-ownership.py`) - are owned by
`docs/agent-extension-pack.md`; read them there (link, do not
restate).

## Subagents

Two subagents ship (REQ-AI-143): `custom-agent/finance-analyst.md`
and `custom-agent/qa-reviewer.md`. Their contracts live in
`docs/agent-extension-pack.md`; the qa-reviewer is the pack-level
shape of the Review rule below - it reviews, it never merges.

## MCP tools

Four MCP tools ship (REQ-AI-143), one HTTP call each under
`mcp-server/tools/`: add_expense, get_budget_status, list_expenses,
monthly_summary. The permission model (JWT auth, what each tool may
touch) is owned by `docs/permissions.md` - link, do not restate.

The pack counts in this file are anchored to the directories, not to
prose, measured at build time: 3 skills (`agent-capabilities/`),
2 hooks (`agent-hooks/*.py`), 4 MCP tools (`mcp-server/tools/*.py`
minus `__init__`), 2 subagents (`custom-agent/*.md`) - i.e. three
skills, two hooks, four MCP tools, two subagents, the same 3/2/4/2
that `docs/agent-extension-pack.md` pins via the stored merge gates;
the two documents may not disagree.

## Review

The rule, stated once and enforced everywhere (REQ-AI-132): **every
agent output requires human review** before it counts. In this repo
"human review" is operationalized, not aspirational: a builder branch
is never self-accepted - an independent verifier role re-executes the
pinned commands at the branch tip, and only the orchestrator merges.
Every Session record above carries its review line for exactly this
reason. What agents may produce at all (and what they may never
touch) is specified in `docs/agent-extension-pack.md` and
`docs/permissions.md`.

## Data policy

The local-only rule (REQ-AI-130): all code, prompts and context stay
on the local machine; nothing is sent to a cloud LLM provider - the
model itself runs locally. What the agent can see and produce is
scoped by `docs/permissions.md`; the authoritative tool data policy is
`security/ai-tool-data-policy.md` - link, do not duplicate (REQ-AI-131
covers "what the agent sees", REQ-AI-132 "what it produces", both
summarized under the Review rule above). This document itself carries
no credentials: no JWT-shaped strings, no token-shaped strings, no
DSN with an inline password - the gitleaks-clean invariant recorded in
`docs/criteria/security_ops_verification.md` is the machine backstop.

## Scan timing

REQ-SEC-072 is the only requirement whose Verification field reads
"Read docs/ai-workflow.md" - this section is that target. Five scans,
five timings (REQ-SEC-072 milestones: after auth, after CRUD, after
dashboard, before deployment, after final changes):

| Scan | Timing against the milestones |
| --- | --- |
| gitleaks | after auth (first secrets surface), then every milestone; results committed |
| semgrep | after CRUD and after dashboard (code-shape rules on new service layers) |
| trivy | before deployment (filesystem vuln + misconfig sweep of the deployable tree) |
| pip-audit | after final changes (backend dependency set closes only there) |
| npm audit | after final changes (frontend dependency set closes only there) |

- **Entry point**: the on-demand aggregate `make security` runs all
  five (REQ-SEC-071); the per-tool targets `security-gitleaks`,
  `security-semgrep`, `security-trivy`, `security-pip-audit`,
  `security-npm-audit` are defined in the Makefile, whose scan
  targets and output paths are the REQ-SEC-071 Verification pair
  (`Makefile` and `security/`).
- **Results are committed reports**: every scan writes its report
  under `security/` and the report is a committed artifact, so the
  evidence survives the machine that produced it.
- **Scans are NOT in CI** (REQ-CICD-073): they run locally and only
  their results are committed; the four workflow files under
  `.github/workflows/` invoke no scan.
- **Deferral closure**: this section is the live_check target of the
  `SCAN_TIMING_DOC` row in t41's deferral register (stored in
  `docs/criteria/security_ops_verification.md`, re-executed by the
  t41 merge gate). The row itself stays DEFERRED in t41's committed
  evidence - no back-editing closed cards - and t53 re-tests and
  closes it in the new register. See
  `docs/criteria/security_ops_verification.md` for the register and
  the scan-jobs-in-CI count it stores.

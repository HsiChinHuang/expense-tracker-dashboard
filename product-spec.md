# Product Specification - expense-tracker-dashboard

This is the product specification required by REQ-DOC-011. Per REQ-DOC-080
(minimal root documentation) it stays a short, navigable spec: every section
anchors its requirements by id into `docs/requirements.md` and the chapter
files under `docs/requirements/` rather than duplicating requirement text.
The reviewer entry point for this repository is `README.md` - start there
for the criteria mapping, the evidence checklist, and both five-minute
verification paths.

## Problem statement

People who track household spending need one place to record expenses, set a
monthly budget, and see where the money went without spreadsheets or manual
charting. The product is a small self-hosted web application: register, log
expenses against categories, set one budget per month, and read a dashboard
of the month's numbers. The measurable problem, permission, and success
goals are specified by Chapter 1 (REQ-PROJ-001..REQ-PROJ-009); this file
does not restate them.

## Target users

- Individual users and small households tracking monthly spending (the
  persona and privacy constraints carry the ids REQ-PROJ-002/003).
- A peer reviewer who must be able to deploy and verify the whole product
  in minutes (REQ-PROJ-009; see the five-minute paths in `README.md`).

Target-user analysis is anchored in Chapter 1 (REQ-PROJ-001..009); user
roles and account behaviour are specified in Chapter 4 (REQ-PROD-001..007).

## User stories

The user-facing flows - register and log in, manage categories, create and
edit expenses, set the monthly budget, read the dashboard, switch months,
and log out - are each specified as numbered requirements in Chapter 4
(REQ-PROD-001..REQ-PROD-007) with acceptance detail in
`docs/requirements/Chapter4_ProductRequirements.md`. The dashboard read
model behind the five charts is REQ-PROD-043 and the six
`/api/v1/dashboard/*` contract paths (see `openapi.yaml`).

## Functional requirements

Authentication, categories, expenses, budgets, audit logging, and the
dashboard aggregations (summary, by-category, trend, cumulative, heatmap,
recent) are enumerated in Chapter 4: REQ-PROD-001..REQ-PROD-007 for the
core flows and REQ-PROD-043 for the dashboard surface. API-level detail
lives in Chapter 8 (REQ-API-001..REQ-API-114) and is exported verbatim to
`openapi.yaml`; this file intentionally does not copy those texts.

## Non-functional requirements

Performance, reliability, security, and portability constraints are
anchored to the Chapter 2 technology baseline and its follow-on chapters:
the range REQ-TECH-001 through REQ-ARCH-082 (stack selection, architecture,
containerization, and deployment constraints). The measured, time-boxed
budget-query timings are recorded in `docs/criteria/dashboard_verification.md`.

## Edge cases

- Empty month: every dashboard query must answer with zeros or empty
  collections rather than errors (REQ-PROD-043 and the contract in
  `openapi.yaml`).
- Over-budget month: the summary must expose the over-budget flag and the
  percentage without hiding the remaining amount.
- Contiguous-month gaps: the trend fills empty months (REQ-PROD-043).
- Expired free-tier database and cold starts: the fallback/recovery record
  is `ops/deployment-health.md`; the operator procedure is `ops/runbook.md`.

## Success criteria

Success is the Chapter 24 acceptance surface, not a new standard invented
here: the Chapter 24.3 quality-acceptance table (15 rows) and the Chapter
24.5 final-project criteria (14 criteria) are mapped row by row to evidence
files in `README.md` (Criteria mapping and Evidence checklist sections,
REQ-DOC-081/REQ-DOC-072). The timed, reproducible dashboard evidence is
`docs/criteria/dashboard_verification.md`.

## Scope boundaries

In scope: the single-user expense tracker described by Chapters 1-4 and the
deployment/operations surface of Chapters 13-14. Out of scope: multi-currency,
shared/household budgets, mobile native clients, reporting exports, and
multi-tenant hosting - none of these appear in `docs/requirements.md` and
none are built. Per REQ-DOC-080 this file, `README.md`, `CLAUDE.md`,
`AGENTS.md`, and `openapi.yaml` are the complete minimal root-document set;
everything deeper lives under `docs/`, `ops/`, or `security/`.

# Verification guide

This document is the relocation home for the reviewer-facing verification
detail that `README.md` carried until t66. The README keeps its own compact
copies of the checklist and the five-minute paths, because the carried
README-scoped gates read those tables from `README.md` itself; this file is
the expanded copy a reviewer opens when the README row is not enough.

## Sections absorbed from README.md

| README section absorbed | What moved here |
|---|---|
| `Evidence checklist` | The expanded reading of the Chapter 24.5 criteria rows |
| `Live verification in five minutes` | The live-path procedure and its measured-status statement |
| `Local verification in five minutes` | The local-path procedure with the full command block |

## Evidence checklist

The Chapter 24.5 evidence checklist in `README.md` maps each of the fourteen
final-project criteria to the file a reviewer opens. Read it together with
`docs/criteria/docs_verification.md`, the deferral register that carries the
DEFERRED status for every verification this environment cannot measure.

## Live verification in five minutes

Reviewer procedure against the deployed URL. Status, stated honestly: the
public Render URL is DEFERRED for live attestation - this environment has no
egress and the stored register records RENDER_DEPLOY, UPTIMEROBOT_MONITOR and
LIVE_COLD_START as deferred (egress_forbidden), so this document records the
procedure without claiming the deployment was verified live in CI. Open the
deployed URL early: the free tier pays a cold start after each idle gap.

1. Open the live URL (the Render service named in `render.yaml`).
2. Register an account (or log in).
3. Add an expense.
4. Set a budget for the month.
5. Verify the five charts (trend, cumulative, by-category pie, weekly
   heatmap, and the KPI/recent surface) render from their own queries.
6. Switch month - every month-driven chart refetches.
7. Log out.

## Local verification in five minutes

The same seven steps with zero accounts:

```bash
git clone <repo-url> && cd expense-tracker-dashboard
cp .env.example .env
docker compose up --build
```

1. Open http://localhost:8000 (the SPA plus the API in one container).
2. Register an account.
3. Add an expense.
4. Set a budget for the month.
5. Verify the five charts.
6. Switch month.
7. Log out, then `docker compose down`.

The npm path reaches the same state without Docker: `npm run check`,
`cp .env.example .env`, `npm run setup:local`, `npm run dev`, then
`npm run stop` (see the README Quick Start).

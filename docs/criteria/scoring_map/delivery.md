# Scoring-map verification record - delivery dimensions

Milestone: phase_20_readme_scoring_map. Card: t114 (platform issue 120).
This file is t114's entire deliverable and the evidence record the README Part 2
table cites. Every claim was re-measured by the builder against the shipped tree
at build time (main 3bfa1f2, 2026-10-23); the card's fences re-measure each one,
so a path or count that moves without this record moving turns a fence RED
rather than leaving a stale claim standing.

Honesty rule (binding on every line): a claim is allowed only if a reader can
check it within 30 seconds at the named First entry point. Where a fact lives
outside git (a hosted URL, a GitHub Environment setting), the record names the
probe or the setting and says it cannot be verified from the tree.

## Deployment

- Claim: 2/2
- Reason: the app is live at the public URL https://expense-tracker-dashboard-1qtu.onrender.com - verified 2026-10-22 (WAL 1265): root serves the SPA document, the hashed JS asset answers 200, /login falls back to the SPA document, and /api/v1/health answers 200 with the postgresql health body; a reader checks the whole claim with one curl of the health URL, and the infrastructure-as-code half of the deploy lives in the one-file render.yaml blueprint next to it.
- First entry point: `https://expense-tracker-dashboard-1qtu.onrender.com/api/v1/health`
- Evidence: `render.yaml`, `ops/deployment-health.md`, `README.md`
- Deep dive: `ops/deployment-health.md`

## CI/CD

- Claim: 3/3
- Reason: three shipped pipelines cover points one and two of the scale - ci.yml runs the lint/type/test suite on pull_request and push, e2e.yml runs the Playwright suite on main pushes only, and deploy.yml is automatic CD gated on a green E2E run (workflow_run trigger) that POSTs a hook held only in the RENDER_DEPLOY_HOOK secret and then verifies /api/v1/health with a bounded retry, so CD means deployed and verified, not curl fired; all three workflows set permissions: contents: read (least privilege). The third point (CD to dev AND a manual production deploy) is ruled SATISFIED at this project scale by the operator ruling of 2026-10-24 (orchestrator WAL entry 1291): the automatic flow deploy.yml carries the dev cadence and the human-gated production pipeline .github/workflows/promote.yml (a workflow_dispatch deploy that consumes the GitHub Environment named production with required reviewers, which the operator created in repository Settings - a Settings artifact that cannot be verified from the tree) carries the production gate, rehearsed green in Actions run 39933068472 (WAL 1281) with the gate demonstrably exercised; the re-baseline to 3/3 prices that logical separation and no more.
- First entry point: `.github/workflows/ci.yml`
- Evidence: `.github/workflows/ci.yml`, `.github/workflows/e2e.yml`, `.github/workflows/deploy.yml`, `Makefile`, `docs/criteria/infra_verification.md`
- Deep dive: `docs/criteria/infra_verification.md`
- Gap (dated ruling record, 2026-10-24, orchestrator WAL entry 1291): the operator ruled verbatim that environment separation is LOGICAL (two pipelines, two gates, one Render target), NOT infrastructural, and under that ruling rubric point 3 is satisfied at this project scale - deploy.yml is the automatic (de facto dev) flow and .github/workflows/promote.yml is the human-gated production pipeline consuming the GitHub Environment production with required reviewers, rehearsed green in Actions run 39933068472 (WAL 1281); the ruling is an interpretation, not a measurement, and no second deployed target exists or is claimed here - render.yaml declares exactly one web service plus one database and both pipelines deploy to that one target.

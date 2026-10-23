# Scoring-map verification record - application dimensions

Milestone: phase_20_readme_scoring_map. Card: t113 (platform issue 119).
This file is t113's entire deliverable and the evidence record the README Part 2
table cites. Every claim was re-measured by the builder against the shipped tree
at build time (main 6faa700, 2026-10-23); the card's fences re-measure each one,
so a path or count that moves without this record moving turns a fence RED
rather than leaving a stale claim standing.

Honesty rule (binding on every line): a claim is allowed only if a reader can
check it within 30 seconds at the named First entry point. Counts of growing
artifacts are stated as date-stamped floors, never as present-tense numbers.
Where a claim depends on running something the verification environment cannot
run (a listening dev server, a docker daemon), the entry point is the file that
defines the single command and the Reason names the strongest evidence that IS
checkable there.

## Application

- Claim: 2/2
- Reason: the root package.json defines the single command npm run dev (dev.ts starts the backend on :8000 and the frontend on :5173 in one interleaved stream), README's Quick Start step 4 is that one command, and the seeded demo path npm run seed:demo is one command too - both scripts are readable in the entry point in well under 30 seconds.
- First entry point: `package.json`
- Evidence: `package.json`, `README.md`, `scripts/dev/dev.ts`, `backend/app/scripts/seed_demo.py`, `docs/requirements/Chapter3_TechStack.md`
- Deep dive: `README.md`

## Testing

- Claim: 2/2
- Reason: unit and integration tiers are separate directories that both exist and are non-empty (measured 2026-10-23: at least 41 backend test files, 24 under backend/tests/unit and 17 under backend/tests/integration), the frontend tier runs vitest, and the single-command surface is make test (uv run pytest for the backend, npm test -- --run for the frontend) - the same Makefile targets ci.yml executes as its unit, integration and frontend jobs, so 'pass' is attestable outside this machine.
- First entry point: `Makefile`
- Evidence: `Makefile`, `backend/tests/unit`, `backend/tests/integration`, `frontend/package.json`, `.github/workflows/ci.yml`, `docs/requirements/Chapter11_TestingStrategy.md`
- Deep dive: `docs/requirements/Chapter11_TestingStrategy.md`

## Containerization

- Claim: 2/2
- Reason: docker-compose.yml carries exactly two services - db on postgres:16-alpine with a healthcheck and a named volume, and app gated on db being healthy - so the full system including the database comes up with the single documented command docker compose up --build, which README's Local verification in five minutes section states; ci.yml's compose-build job executes docker compose build on every CI run, so the compose surface is machine-attested rather than asserted.
- First entry point: `docker-compose.yml`
- Evidence: `docker-compose.yml`, `Dockerfile`, `README.md`, `.github/workflows/ci.yml`, `docs/criteria/infra_verification.md`
- Deep dive: `docs/criteria/infra_verification.md`

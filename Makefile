# Expense Tracker Dashboard — root task runner (REQ-DOC-051).
# Targets delegate to the toolchains documented in docs/commands.md:
# backend -> uv (Linux binary), frontend -> npm (Windows binaries under WSL).

.PHONY: setup setup-backend setup-frontend dev dev-backend dev-frontend \
        test test-backend test-backend-unit test-backend-integration test-backend-cov \
        test-frontend test-frontend-cov lint lint-backend lint-frontend \
        down migrate seed e2e security

# Resolve the frontend directory relative to this Makefile (worktree-safe).
FRONTEND_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))frontend)

# On WSL, node/npm are Windows executables and cannot run from a WSL cwd
# directly (t2 precedent); route frontend recipes through cmd.exe there.
ifeq ($(wildcard /proc/sys/fs/binfmt_misc/WSLInterop),)
FE = cd frontend && $(1)
else
FE_WIN_DIR := $(shell wslpath -w $(FRONTEND_DIR))
FE = cmd.exe /c "cd /d $(FE_WIN_DIR) && $(1)"
endif

# --- Setup ---

setup: setup-backend setup-frontend

setup-backend:
	cd backend && uv sync

setup-frontend:
	$(call FE,npm install)

# Install frontend deps only when missing (idempotent prerequisite).
frontend-deps:
	@test -d frontend/node_modules || $(call FE,npm install)

# --- Development servers ---

dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in two terminals."

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload

dev-frontend: frontend-deps
	$(call FE,npm run dev)

# --- Tests ---

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest

test-frontend: frontend-deps
	$(call FE,npm test -- --run)

# Split backend runs for CI (REQ-TEST-050): unit and integration layers.
test-backend-unit:
	cd backend && uv run pytest tests/unit

test-backend-integration:
	cd backend && uv run pytest tests/integration

# Coverage runs for CI (REQ-TEST-050): --cov backend / --coverage frontend.
test-backend-cov:
	cd backend && uv run pytest --cov=app --cov-report=term-missing

test-frontend-cov: frontend-deps
	$(call FE,npm test -- --run --coverage)

# --- Lint ---

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run ruff check .
	cd backend && uv run mypy .

lint-frontend: frontend-deps
	$(call FE,npm run lint)
	$(call FE,npx tsc --noEmit)

# --- Lifecycle and later-phase stubs (targets exist now; see docs/issues/t4.md) ---

down:
	@echo "No services to stop yet (docker-compose lands in phase_5_infra)."

migrate:
	@mkdir -p build  # ensure the gitignored build/ dir exists for tmp DATABASE_URLs (t5 ac5)
	cd backend && uv run alembic upgrade head

seed:
	@echo "Seed data script lands in phase_3."

# Real Playwright harness target (REQ-TEST-050): the pinned dependency is
# installed with npm install --no-save (W6 ruling - the e2e lockfile is NOT
# committed, so the earlier "# ... npm ci" draft recipe is forbidden: npm ci
# fails hard without a lockfile), then the suite runs with the HTML report.
e2e:
	cd e2e && npm install --no-save
	cd e2e && npx playwright test

# Real local scan pipeline (REQ-SEC-070/071, REQ-TECH-074, REQ-DOC-051; t36).
# Five sub-targets, each fetching its pinned tool at gate time into
# $HOME/.local/bin (BANNED from the git tree) and writing its frozen security/
# report path. Reports are COMMITTED artifacts (never gitignored). The scans
# are local-only: no CI job is added (REQ-CICD-073/083).
security: security-gitleaks security-semgrep security-trivy security-pip-audit security-npm-audit
	@echo "Five scan reports written under security/ (REQ-SEC-070)."

# gitleaks v8.30.1 linux-x64, tracked-tree sweep (git ls-files -> temp dir).
# The gate-time allowlist config (NEVER committed) extends the pinned v8.30.1
# default config with four narrow match-anchored regexes covering the five
# measured false-positive matches on the tracked tree (two of the five findings
# share one match text). Rationale: t36 groom handoff + the t40 accepted-
# findings register. Override points for gate dry-runs: GITLEAKS_CONFIG,
# GITLEAKS_SRC, GITLEAKS_REPORT.
security-gitleaks:
	@bash -c 'export PATH="$$HOME/.local/bin:$$PATH"; command -v gitleaks >/dev/null 2>&1 || { curl -fsSL -o /tmp/t36-gitleaks.tgz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz && tar -xzf /tmp/t36-gitleaks.tgz -C /tmp gitleaks && install -m 0755 /tmp/gitleaks "$$HOME/.local/bin/gitleaks"; } || exit 1; gitleaks version | tr -d "\r" | head -1 | grep -qE "^8[.]30[.]1" || exit 1; cfg="$${GITLEAKS_CONFIG:-/tmp/t36-gitleaks-config.toml}"; curl -fsSL -o "$$cfg" https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml || exit 1; n=$$(grep -n "^id = \"generic-api-key\"" "$$cfg" | head -1 | cut -d: -f1); [ -n "$$n" ] || exit 1; r=$$(tail -n +"$$n" "$$cfg" | grep -n "^]" | head -1 | cut -d: -f1); [ -n "$$r" ] || exit 1; m=$$((n+r-1)); { head -n "$$m" "$$cfg"; printf "%s\n" "" "[[rules.allowlists]]" "description = \"t36: four narrow match-anchored regexes covering five measured false-positive matches on the tracked tree (negative-controlled; rationale: t36 groom handoff and the t40 accepted-findings register)\"" "regexTarget = \"match\"" "regexes = [" "    \"password.{0,4}.verification123\"," "    \"tokens, elapsed=0[.]142\"," "    \"access_token.{0,4}.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[.][.][.]\"," "    \"test_health_api[.]py == 2b71b7feab4152d1804b66e11dc0f3882bacb684\"" "]"; tail -n +$$((m+1)) "$$cfg"; } > "$$cfg.merged" && mv "$$cfg.merged" "$$cfg" || exit 1; src="$${GITLEAKS_SRC:-$$(mktemp -d)}"; mkdir -p "$$src" || exit 1; G=$$(wslpath -w "$$PWD"); fl=$$(mktemp); cmd.exe /c "git -C $$G ls-files" 2>/dev/null | tr -d "\r" > "$$fl" || exit 1; [ -s "$$fl" ] || exit 1; tar -cf - -T "$$fl" 2>/dev/null | tar -xf - -C "$$src" || exit 1; rm -f "$$fl"; rep="$${GITLEAKS_REPORT:-security/gitleaks-report.json}"; gitleaks detect --no-git --source "$$src" --config "$$cfg" --report-format json --report-path "$$rep"; rc=$$?; echo "gitleaks sweep rc=$$rc report=$$rep"; exit $$rc'

# semgrep via uvx (mutable rules; version recorded by the tool itself).
security-semgrep:
	@bash -c 'export PATH="$$HOME/.local/bin:$$PATH"; command -v uvx >/dev/null 2>&1 || exit 1; uvx semgrep --version >/dev/null 2>&1 || exit 1; out="$${SEMGREP_REPORT:-security/semgrep-report.json}"; uvx semgrep --config auto --json --quiet --output "$$out" .; rc=$$?; { [ "$$rc" -eq 0 ] || [ "$$rc" -eq 1 ]; } || exit 1; echo "semgrep report written: $$out (rc=$$rc)"'

# trivy v0.75.0 (trivy_0.75.0_Linux-64bit.tar.gz) fs vuln+misconfig scan.
security-trivy:
	@bash -c 'export PATH="$$HOME/.local/bin:$$PATH"; command -v trivy >/dev/null 2>&1 || { curl -fsSL -o /tmp/t36-trivy.tgz https://github.com/aquasecurity/trivy/releases/download/v0.75.0/trivy_0.75.0_Linux-64bit.tar.gz && tar -xzf /tmp/t36-trivy.tgz -C /tmp trivy && install -m 0755 /tmp/trivy "$$HOME/.local/bin/trivy"; } || exit 1; out="$${TRIVY_REPORT:-security/trivy-report.json}"; trivy fs --scanners vuln,misconfig --format json --output "$$out" .; rc=$$?; [ "$$rc" -eq 0 ] || exit 1; echo "trivy report written: $$out"'

# pip-audit via uvx over the repo's own uv export (requirement-line floor 50;
# findings recorded, never suppressed: tool rc 0 or 1 both accepted).
security-pip-audit:
	@bash -c 'export PATH="$$HOME/.local/bin:$$PATH"; command -v uv >/dev/null 2>&1 || exit 1; req="$${PIP_AUDIT_REQUIREMENTS:-/tmp/t36-pip-audit-requirements.txt}"; (cd backend && uv export --no-hashes --frozen --format requirements-txt) > "$$req" 2>/dev/null || exit 1; n=$$(grep -cE "^[A-Za-z0-9._-]+==" "$$req"); echo "pip-audit requirement lines: $$n (floor 50)"; [ "$$n" -ge 50 ] || exit 1; out="$${PIP_AUDIT_REPORT:-security/pip-audit-report.txt}"; (cd backend && uvx pip-audit -r "$$req") > "$$out" 2>&1; rc=$$?; { [ "$$rc" -eq 0 ] || [ "$$rc" -eq 1 ]; } || exit 1; grep -qE "Found [0-9]+ known vulnerabilit|No known vulnerabilit" "$$out" || exit 1; echo "pip-audit report written: $$out (tool rc=$$rc, findings recorded never suppressed)"'

# npm audit via cmd.exe from frontend/ (READ-ONLY: no audit fix, no install).
security-npm-audit:
	@bash -c 'D=$$(wslpath -w "$$PWD/frontend"); out="$${NPM_AUDIT_REPORT:-security/npm-audit-report.txt}"; cmd.exe /c "cd /d $$D && npm.cmd audit" > "$$out" 2>&1; rc=$$?; { [ "$$rc" -eq 0 ] || [ "$$rc" -eq 1 ]; } || exit 1; grep -qE "[0-9]+ vulnerabilit" "$$out" || exit 1; echo "npm-audit report written: $$out (read-only audit, tool rc=$$rc)"'

.PHONY: security-gitleaks security-semgrep security-trivy security-pip-audit security-npm-audit

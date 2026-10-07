# Expense Tracker Dashboard — root task runner (REQ-DOC-051).
# Targets delegate to the toolchains documented in docs/commands.md:
# backend -> uv (Linux binary), frontend -> npm (Windows binaries under WSL).

.PHONY: setup setup-backend setup-frontend dev dev-backend dev-frontend \
        test test-backend test-frontend lint lint-backend lint-frontend \
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
	@echo "Alembic migrations land in phase_2; run 'cd backend && uv run alembic upgrade head' then."

seed:
	@echo "Seed data script lands in phase_3."

e2e:
	@echo "Playwright e2e harness lands in phase_5_infra."

security:
	@echo "gitleaks/semgrep/trivy scans land in phase_7_security_ops."

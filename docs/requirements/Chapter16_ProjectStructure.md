# Chapter 16: Project Structure

## 16.1 Complete Repository Tree

```
expense-tracker-dashboard/
│
├── README.md
├── product-spec.md
├── AGENTS.md
├── CLAUDE.md
├── openapi.yaml
├── LICENSE
├── Makefile
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── render.yaml
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── e2e.yml
│       └── deploy.yml
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── queryKeys.ts
│   │   │   ├── auth.ts
│   │   │   ├── categories.ts
│   │   │   ├── expenses.ts
│   │   │   ├── budgets.ts
│   │   │   ├── dashboard.ts
│   │   │   └── health.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   ├── Skeleton.tsx
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── Badge.tsx
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── MonthPicker.tsx
│   │   │   ├── charts/
│   │   │   │   ├── CategoryPieChart.tsx
│   │   │   │   ├── CategoryPieChart.test.tsx
│   │   │   │   ├── MonthlyTrendChart.tsx
│   │   │   │   ├── CumulativeLineChart.tsx
│   │   │   │   ├── WeeklyHeatmap.tsx
│   │   │   │   ├── WeeklyHeatmap.test.tsx
│   │   │   │   ├── BudgetProgress.tsx
│   │   │   │   └── BudgetProgress.test.tsx
│   │   │   ├── forms/
│   │   │   │   ├── ExpenseForm.tsx
│   │   │   │   ├── ExpenseForm.test.tsx
│   │   │   │   ├── BudgetForm.tsx
│   │   │   │   ├── CategoryForm.tsx
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   └── common/
│   │   │       ├── EmptyState.tsx
│   │   │       ├── ErrorState.tsx
│   │   │       ├── LoadingState.tsx
│   │   │       ├── ConfirmDialog.tsx
│   │   │       └── ProtectedRoute.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── LoginPage.test.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ExpensesPage.tsx
│   │   │   ├── BudgetPage.tsx
│   │   │   ├── CategoriesPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useCategories.ts
│   │   │   ├── useExpenses.ts
│   │   │   ├── useBudgets.ts
│   │   │   ├── useDashboard.ts
│   │   │   └── useToast.ts
│   │   ├── context/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── MonthContext.tsx
│   │   │   └── ToastContext.tsx
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   └── domain.ts
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   ├── format.test.ts
│   │   │   ├── date.ts
│   │   │   ├── date.test.ts
│   │   │   ├── validation.ts
│   │   │   ├── validation.test.ts
│   │   │   └── color.ts
│   │   └── test/
│   │       ├── setup.ts
│   │       ├── mocks/
│   │       │   ├── handlers.ts
│   │       │   └── server.ts
│   │       └── fixtures/
│   │           └── categories.ts
│   ├── public/
│   │   └── favicon.svg
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── expense.py
│   │   │   ├── budget.py
│   │   │   └── audit_log.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── auth.py
│   │   │   ├── category.py
│   │   │   ├── expense.py
│   │   │   ├── budget.py
│   │   │   └── dashboard.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── categories.py
│   │   │   ├── expenses.py
│   │   │   ├── budgets.py
│   │   │   ├── dashboard.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── category_service.py
│   │   │   ├── expense_service.py
│   │   │   ├── budget_service.py
│   │   │   └── dashboard_service.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py
│   │   │   ├── password.py
│   │   │   └── dependencies.py
│   │   ├── audit/
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── errors.py
│   │   │   └── logging.py
│   │   └── scripts/
│   │       ├── __init__.py
│   │       └── seed.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_password.py
│   │   │   ├── test_jwt.py
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_category_service.py
│   │   │   ├── test_expense_service.py
│   │   │   ├── test_budget_service.py
│   │   │   ├── test_dashboard_service.py
│   │   │   ├── test_audit_logger.py
│   │   │   └── test_decimal_helpers.py
│   │   └── integration/
│   │       ├── __init__.py
│   │       ├── test_auth_api.py
│   │       ├── test_categories_api.py
│   │       ├── test_expenses_api.py
│   │       ├── test_budgets_api.py
│   │       ├── test_dashboard_api.py
│   │       ├── test_isolation.py
│   │       ├── test_health_api.py
│   │       └── test_agent_hooks.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_seed_categories.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
│
├── e2e/
│   ├── tests/
│   │   ├── happy-path.spec.ts
│   │   ├── isolation.spec.ts
│   │   └── month-switch.spec.ts
│   ├── fixtures/
│   │   ├── users.ts
│   │   └── helpers.ts
│   ├── playwright.config.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── process.md
│   ├── ai-workflow.md
│   ├── design-system.md
│   ├── testing-guidelines.md
│   ├── agent-extension-pack.md
│   ├── permissions.md
│   ├── task-template.md
│   └── team/
│       ├── pm.md
│       ├── software-engineer.md
│       └── qa-engineer.md
│
├── security/
│   ├── pr-audit.md
│   ├── gitleaks-report.json
│   ├── semgrep-report.json
│   ├── trivy-report.json
│   ├── pip-audit-report.txt
│   ├── npm-audit-report.txt
│   ├── agent-security-notes.md
│   └── ai-tool-data-policy.md
│
├── ops/
│   ├── runbook.md
│   ├── health-check.md
│   ├── diagnosis.md
│   ├── logging.md
│   └── deployment-health.md
│
├── agent-capabilities/
│   ├── monthly-report/
│   │   └── SKILL.md
│   ├── add-expense/
│   │   └── SKILL.md
│   └── budget-check/
│       └── SKILL.md
│
├── agent-hooks/
│   ├── __init__.py
│   ├── validate-amount.py
│   ├── validate-ownership.py
│   └── README.md
│
├── mcp-server/
│   ├── server.py
│   ├── auth.py
│   ├── config.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── add_expense.py
│   │   ├── get_budget_status.py
│   │   ├── monthly_summary.py
│   │   └── list_expenses.py
│   ├── pyproject.toml
│   └── README.md
│
├── custom-agent/
│   ├── finance-analyst.md
│   └── qa-reviewer.md
│
├── .agents/
│   ├── skills/
│   │   ├── monthly-report -> ../../agent-capabilities/monthly-report
│   │   ├── add-expense -> ../../agent-capabilities/add-expense
│   │   └── budget-check -> ../../agent-capabilities/budget-check
│   └── agents/
│       ├── finance-analyst.md -> ../../custom-agent/finance-analyst.md
│       └── qa-reviewer.md -> ../../custom-agent/qa-reviewer.md
│
└── screenshots/
    ├── dashboard.png
    ├── expense-form.png
    ├── budget-page.png
    └── health-check.png
```

## 16.2 Directory Responsibilities

### 16.2.1 Top-Level Directories

| Directory | Responsibility | Owned By |
|---|---|---|
| `frontend/` | React SPA | Frontend developer |
| `backend/` | FastAPI application | Backend developer |
| `e2e/` | Playwright tests | QA |
| `docs/` | Documentation | Whole team |
| `security/` | Security artifacts | Security reviewer |
| `ops/` | Operations artifacts | Operator |
| `agent-capabilities/` | Skills | Agent author |
| `agent-hooks/` | Guardrails | Agent author |
| `mcp-server/` | MCP tools | Agent author |
| `custom-agent/` | Subagents | Agent author |
| `.agents/` | Symlinks for discovery | Agent tooling |
| `screenshots/` | UI screenshots | Whole team |
| `.github/workflows/` | CI/CD | DevOps |

### 16.2.2 Frontend Subdirectories

| Directory | Responsibility |
|---|---|
| `src/api/` | HTTP client and resource modules |
| `src/components/ui/` | Reusable primitive components |
| `src/components/layout/` | Layout components |
| `src/components/charts/` | Chart components |
| `src/components/forms/` | Form components |
| `src/components/common/` | Shared components |
| `src/pages/` | Route-level components |
| `src/hooks/` | Data hooks |
| `src/context/` | Global state providers |
| `src/types/` | TypeScript types |
| `src/utils/` | Pure utility functions |
| `src/test/` | Test setup and mocks |

### 16.2.3 Backend Subdirectories

| Directory | Responsibility |
|---|---|
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request and response schemas |
| `app/routers/` | HTTP endpoints |
| `app/services/` | Business logic |
| `app/auth/` | JWT and password handling |
| `app/audit/` | Audit log writer |
| `app/core/` | Errors, logging, shared utilities |
| `app/scripts/` | Utility scripts (seed, etc.) |
| `tests/unit/` | Unit tests |
| `tests/integration/` | Integration tests |
| `alembic/` | Database migrations |

## 16.3 File Purpose Reference

### 16.3.1 Root Files

| File | Purpose | Criterion |
|---|---|---|
| README.md | Reviewer entry point | 1, 14 |
| product-spec.md | Full product specification | 1 |
| AGENTS.md | Agent context | 2, 12 |
| CLAUDE.md | Points to AGENTS.md | 2 |
| openapi.yaml | API contract | 5 |
| LICENSE | MIT license | - |
| Makefile | Common commands | 14 |
| .env.example | Environment variable template | 14 |
| .gitignore | Excludes secrets and build artifacts | 13 |
| Dockerfile | Multi-stage build | 8 |
| docker-compose.yml | Local full-stack | 8 |
| render.yaml | Deployment configuration | 10 |

### 16.3.2 CI/CD Workflows

| File | Purpose | Criterion |
|---|---|---|
| ci.yml | Run tests on PR | 11 |
| e2e.yml | Run E2E on main | 9, 11 |
| deploy.yml | Deploy to Render after E2E | 11 |

### 16.3.3 Frontend Files

| File | Purpose |
|---|---|
| main.tsx | React entry point, provider nesting |
| App.tsx | Route definitions |
| index.css | Tailwind imports |
| api/client.ts | Axios instance, interceptors |
| api/queryKeys.ts | Query key factory |
| api/auth.ts | Auth endpoints |
| api/categories.ts | Category endpoints |
| api/expenses.ts | Expense endpoints |
| api/budgets.ts | Budget endpoints |
| api/dashboard.ts | Dashboard endpoints |
| api/health.ts | Health endpoint |
| components/ui/Button.tsx | Reusable button |
| components/ui/Card.tsx | Reusable card |
| components/ui/Input.tsx | Reusable input |
| components/ui/Select.tsx | Reusable select |
| components/ui/Modal.tsx | Modal dialog |
| components/ui/Toast.tsx | Toast notification |
| components/ui/Skeleton.tsx | Loading skeleton |
| components/ui/Spinner.tsx | Loading spinner |
| components/ui/Badge.tsx | Badge |
| components/layout/AppShell.tsx | Main layout |
| components/layout/Sidebar.tsx | Sidebar navigation |
| components/layout/Header.tsx | Top header |
| components/layout/MonthPicker.tsx | Month selector |
| components/charts/CategoryPieChart.tsx | Pie chart |
| components/charts/MonthlyTrendChart.tsx | Bar chart |
| components/charts/CumulativeLineChart.tsx | Line chart |
| components/charts/WeeklyHeatmap.tsx | Heatmap |
| components/charts/BudgetProgress.tsx | Progress bar |
| components/forms/ExpenseForm.tsx | Expense form |
| components/forms/BudgetForm.tsx | Budget form |
| components/forms/CategoryForm.tsx | Category form |
| components/forms/LoginForm.tsx | Login form |
| components/forms/RegisterForm.tsx | Register form |
| components/common/EmptyState.tsx | Empty state |
| components/common/ErrorState.tsx | Error state |
| components/common/LoadingState.tsx | Loading state |
| components/common/ConfirmDialog.tsx | Confirmation dialog |
| components/common/ProtectedRoute.tsx | Route guard |
| pages/LoginPage.tsx | Login page |
| pages/RegisterPage.tsx | Register page |
| pages/DashboardPage.tsx | Dashboard page |
| pages/ExpensesPage.tsx | Expenses page |
| pages/BudgetPage.tsx | Budget page |
| pages/CategoriesPage.tsx | Categories page |
| pages/NotFoundPage.tsx | 404 page |
| hooks/useAuth.ts | Auth hook |
| hooks/useCategories.ts | Categories hook |
| hooks/useExpenses.ts | Expenses hook |
| hooks/useBudgets.ts | Budgets hook |
| hooks/useDashboard.ts | Dashboard hook |
| hooks/useToast.ts | Toast hook |
| context/AuthContext.tsx | Auth provider |
| context/MonthContext.tsx | Month provider |
| context/ToastContext.tsx | Toast provider |
| types/api.ts | API types |
| types/domain.ts | Domain types |
| utils/format.ts | Formatting functions |
| utils/date.ts | Date helpers |
| utils/validation.ts | Zod schemas |
| utils/color.ts | Color helpers |
| test/setup.ts | Test setup |
| test/mocks/handlers.ts | MSW handlers |
| test/mocks/server.ts | MSW server |
| test/fixtures/categories.ts | Test fixtures |

### 16.3.4 Backend Files

| File | Purpose |
|---|---|
| app/main.py | FastAPI app factory |
| app/config.py | Settings |
| app/database.py | Engine and session |
| app/models/base.py | Base and mixins |
| app/models/user.py | User model |
| app/models/category.py | Category model |
| app/models/expense.py | Expense model |
| app/models/budget.py | Budget model |
| app/models/audit_log.py | Audit log model |
| app/schemas/common.py | Shared schemas |
| app/schemas/auth.py | Auth schemas |
| app/schemas/category.py | Category schemas |
| app/schemas/expense.py | Expense schemas |
| app/schemas/budget.py | Budget schemas |
| app/schemas/dashboard.py | Dashboard schemas |
| app/routers/auth.py | Auth endpoints |
| app/routers/categories.py | Category endpoints |
| app/routers/expenses.py | Expense endpoints |
| app/routers/budgets.py | Budget endpoints |
| app/routers/dashboard.py | Dashboard endpoints |
| app/routers/health.py | Health endpoint |
| app/services/auth_service.py | Auth logic |
| app/services/category_service.py | Category logic |
| app/services/expense_service.py | Expense logic |
| app/services/budget_service.py | Budget logic |
| app/services/dashboard_service.py | Dashboard logic |
| app/auth/jwt.py | JWT sign and verify |
| app/auth/password.py | bcrypt hash and verify |
| app/auth/dependencies.py | Auth dependencies |
| app/audit/logger.py | Audit writer |
| app/core/errors.py | AppError and handlers |
| app/core/logging.py | Logging setup |
| app/scripts/seed.py | Seed system categories |
| tests/conftest.py | Test fixtures |
| alembic/env.py | Alembic config |
| alembic/versions/001_initial_schema.py | Schema migration |
| alembic/versions/002_seed_categories.py | Seed migration |
| pyproject.toml | Python dependencies |
| uv.lock | Locked dependencies |

### 16.3.5 E2E Files

| File | Purpose |
|---|---|
| tests/happy-path.spec.ts | Complete user flow |
| tests/isolation.spec.ts | User data isolation |
| tests/month-switch.spec.ts | Month switching |
| fixtures/users.ts | Unique user generator |
| fixtures/helpers.ts | Reusable test helpers |
| playwright.config.ts | Playwright configuration |

### 16.3.6 Docs Files

| File | Purpose |
|---|---|
| architecture.md | System architecture |
| api.md | API usage guide |
| process.md | Workflow and roles |
| ai-workflow.md | AI-assisted development record |
| design-system.md | UI conventions |
| testing-guidelines.md | Testing rules |
| agent-extension-pack.md | Extension pack overview |
| permissions.md | Permission matrix |
| task-template.md | Issue grooming template |
| team/pm.md | PM agent role |
| team/software-engineer.md | SWE agent role |
| team/qa-engineer.md | QA agent role |

### 16.3.7 Security Files

| File | Purpose |
|---|---|
| pr-audit.md | PR review record |
| gitleaks-report.json | Secret scan output |
| semgrep-report.json | SAST output |
| trivy-report.json | Dependency scan output |
| pip-audit-report.txt | Python dependency scan |
| npm-audit-report.txt | Node dependency scan |
| agent-security-notes.md | Agent security design |
| ai-tool-data-policy.md | AI data policy |

### 16.3.8 Ops Files

| File | Purpose |
|---|---|
| runbook.md | Common problems |
| health-check.md | Health endpoint reference |
| diagnosis.md | Worked diagnosis example |
| logging.md | Log format and events |
| deployment-health.md | Deployment verification |

### 16.3.9 Agent Extension Files

| File | Purpose |
|---|---|
| agent-capabilities/monthly-report/SKILL.md | Monthly report skill |
| agent-capabilities/add-expense/SKILL.md | Add expense skill |
| agent-capabilities/budget-check/SKILL.md | Budget check skill |
| agent-hooks/validate-amount.py | Amount guardrail |
| agent-hooks/validate-ownership.py | Ownership guardrail |
| agent-hooks/README.md | Hook documentation |
| mcp-server/server.py | MCP server entry |
| mcp-server/auth.py | JWT verification |
| mcp-server/config.py | MCP settings |
| mcp-server/tools/add_expense.py | Add expense tool |
| mcp-server/tools/get_budget_status.py | Budget status tool |
| mcp-server/tools/monthly_summary.py | Monthly summary tool |
| mcp-server/tools/list_expenses.py | List expenses tool |
| mcp-server/pyproject.toml | MCP dependencies |
| mcp-server/README.md | MCP documentation |
| custom-agent/finance-analyst.md | Analyst subagent |
| custom-agent/qa-reviewer.md | QA subagent |

### 16.3.10 Symlink Files

| Symlink | Points To | Purpose |
|---|---|---|
| .agents/skills/monthly-report | agent-capabilities/monthly-report | Skill discovery |
| .agents/skills/add-expense | agent-capabilities/add-expense | Skill discovery |
| .agents/skills/budget-check | agent-capabilities/budget-check | Skill discovery |
| .agents/agents/finance-analyst.md | custom-agent/finance-analyst.md | Subagent discovery |
| .agents/agents/qa-reviewer.md | custom-agent/qa-reviewer.md | Subagent discovery |

## 16.4 File Count Summary

| Area | Files |
|---|---|
| Root | 12 |
| CI/CD | 3 |
| Frontend source | ~70 |
| Frontend config | ~12 |
| Backend source | ~50 |
| Backend tests | ~20 |
| Backend config | ~5 |
| E2E | ~7 |
| Docs | ~12 |
| Security | 8 |
| Ops | 5 |
| Agent extension | ~20 |
| Screenshots | 4 |
| **Total** | **~230** |

## 16.5 Naming Conventions

### 16.5.1 Files

| Type | Convention | Example |
|---|---|---|
| React component | PascalCase.tsx | `ExpenseForm.tsx` |
| React hook | camelCase.ts, `use` prefix | `useExpenses.ts` |
| TypeScript module | camelCase.ts | `format.ts` |
| Test file | Same name + `.test.ts(x)` | `format.test.ts` |
| Python module | snake_case.py | `expense_service.py` |
| Python test | `test_` prefix | `test_expenses_api.py` |
| Markdown | kebab-case.md | `ai-workflow.md` |
| JSON report | kebab-case.json | `gitleaks-report.json` |
| Migration | NNN_description.py | `001_initial_schema.py` |

### 16.5.2 Directories

| Type | Convention | Example |
|---|---|---|
| Feature directory | lowercase | `expenses/` |
| Python package | snake_case | `agent_hooks/` (if importable) |
| Agent tool directory | kebab-case | `agent-capabilities/` |
| Docs subdirectory | lowercase | `team/` |

### 16.5.3 Why Mixed Conventions

| Area | Reason |
|---|---|
| Python | PEP 8 requires snake_case |
| React | Community convention is PascalCase |
| Markdown | kebab-case is readable in URLs |
| Agent tools | Match the tool's expected convention |

## 16.6 What Is Not in the Repository

| Excluded | Reason |
|---|---|
| `.env` | Contains secrets |
| `node_modules/` | Installed by npm |
| `.venv/` | Installed by uv |
| `__pycache__/` | Generated by Python |
| `*.db`, `*.sqlite` | Local database files |
| `dist/`, `build/` | Build artifacts |
| `coverage/`, `htmlcov/` | Coverage reports |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Tool caches |
| `.DS_Store` | macOS metadata |
| `*.log` | Runtime logs |
| Real user data | Privacy |
| Production database dumps | Security |
| RENDER_DEPLOY_HOOK | Secret |

## 16.7 Structure Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Monorepo | Single repository | Simpler for a solo project |
| Frontend/backend split | Top-level directories | Clear separation |
| E2E separate from frontend | `e2e/` | Different runtime, different deps |
| Docs in `docs/` | Separate from root | Keeps root clean |
| Security in `security/` | Dedicated directory | Easy for reviewers |
| Ops in `ops/` | Dedicated directory | Easy for reviewers |
| Agent capabilities in own directories | Top-level | Self-documenting |
| Symlinks in `.agents/` | Discovery convention | Agent tool compatibility |
| Screenshots in `screenshots/` | Dedicated directory | Visual evidence |
| Tests next to code | `*.test.ts` beside source | Easy to find |
| Backend tests separate | `tests/unit/` and `tests/integration/` | Clear separation |
| Migrations in `alembic/` | Standard location | Alembic convention |
| No `src/` at root | Directories are top-level | Flat is easier to navigate |
| No nested monorepo tooling | No Turborepo or Nx | Overkill for two packages |
```

---
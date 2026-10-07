# Chapter 17: Development Plan

## 17.1 Overview

The project is built in eight phases. Each phase produces something
concrete and testable. Phases are sequential; each one builds on the
previous.

### 17.1.1 Phase Summary

| Phase | Name | Deliverable | Est. Days |
|---|---|---|---|
| 1 | Spec and Skeleton | product-spec.md, repo structure, AGENTS.md | 2 |
| 2 | Authentication | Register, login, JWT, protected routes | 3 |
| 3 | Core CRUD | Categories, expenses, budgets, audit | 5 |
| 4 | Dashboard | 5 charts, aggregations, month picker | 4 |
| 5 | Container and CI/CD | Docker, GitHub Actions, Render deploy | 3 |
| 6 | Agent Extension Pack | Skills, hooks, MCP, subagents | 3 |
| 7 | Security and Ops | Scans, artifacts, runbook, diagnosis | 2 |
| 8 | Docs and Polish | README, screenshots, final testing | 3 |
| **Total** | | | **25 days** |

### 17.1.2 Phase Dependencies

```
Phase 1: Spec and Skeleton
    │
    ▼
Phase 2: Authentication
    │
    ▼
Phase 3: Core CRUD
    │
    ├──────────────────┐
    ▼                  ▼
Phase 4: Dashboard    Phase 5: Container and CI/CD
    │                  │
    └────────┬─────────┘
             ▼
Phase 6: Agent Extension Pack
    │
    ▼
Phase 7: Security and Ops
    │
    ▼
Phase 8: Docs and Polish
```

Phase 4 and Phase 5 can run in parallel if needed.

## 17.2 Phase 1: Spec and Skeleton

### 17.2.1 Goal

Establish the specification, repository structure, and agent workflow
before writing any application code.

### 17.2.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 1.1 | Write product-spec.md | Full product specification |
| 1.2 | Create repository structure | All directories and placeholder files |
| 1.3 | Write AGENTS.md | Agent context file |
| 1.4 | Write CLAUDE.md | Single line `@AGENTS.md` |
| 1.5 | Write docs/process.md | Workflow and roles |
| 1.6 | Write docs/team/pm.md | PM role |
| 1.7 | Write docs/team/software-engineer.md | SWE role |
| 1.8 | Write docs/team/qa-engineer.md | QA role |
| 1.9 | Write docs/task-template.md | Issue template |
| 1.10 | Create GitHub Issues | ~30 issues from the spec |
| 1.11 | Groom all issues with PM agent | Groomed backlog |
| 1.12 | Initialize backend with uv and a passing test | Backend skeleton |
| 1.13 | Initialize frontend with Vite and a passing test | Frontend skeleton |
| 1.14 | Write .env.example | Environment template |
| 1.15 | Write .gitignore | Git ignore rules |
| 1.16 | Write LICENSE | MIT license |
| 1.17 | Write Makefile | Common commands |

### 17.2.3 Deliverables

- `product-spec.md`
- `AGENTS.md`, `CLAUDE.md`
- `docs/process.md`, `docs/team/*.md`, `docs/task-template.md`
- Repository skeleton with all directories
- GitHub Issues backlog, groomed
- Backend and frontend skeleton with passing tests
- Root config files

### 17.2.4 Verification

| Check | How |
|---|---|
| Spec is complete | Read product-spec.md, all sections filled |
| Backend starts | `cd backend && uv run pytest` passes |
| Frontend starts | `cd frontend && npm test` passes |
| Issues are groomed | Each has Goal, Acceptance Criteria, Out of Scope, Constraints |
| Agent can read context | Ask the agent "what is this project?" and verify it answers from AGENTS.md |

### 17.2.5 Risks

| Risk | Mitigation |
|---|---|
| Spec is too vague | Use the grooming checklist |
| Spec is too detailed | Keep MVP scope; defer extras to out-of-scope issues |
| Too many issues | Merge small ones during grooming |

## 17.3 Phase 2: Authentication

### 17.3.1 Goal

Implement user registration, login, JWT authentication, and protected
routes on both backend and frontend.

### 17.3.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 2.1 | User model and migration | `users` table |
| 2.2 | Password hashing with bcrypt | `app/auth/password.py` |
| 2.3 | JWT signing and verification | `app/auth/jwt.py` |
| 2.4 | Register endpoint | `POST /auth/register` |
| 2.5 | Login endpoint | `POST /auth/login` |
| 2.6 | Current user endpoint | `GET /auth/me` |
| 2.7 | Auth dependency | `get_current_user` |
| 2.8 | Auth unit tests | `test_password.py`, `test_jwt.py`, `test_auth_service.py` |
| 2.9 | Auth integration tests | `test_auth_api.py` |
| 2.10 | Frontend AuthContext | `context/AuthContext.tsx` |
| 2.11 | Axios client with interceptors | `api/client.ts` |
| 2.12 | Login page | `pages/LoginPage.tsx` |
| 2.13 | Register page | `pages/RegisterPage.tsx` |
| 2.14 | ProtectedRoute | `components/common/ProtectedRoute.tsx` |
| 2.15 | Frontend auth tests | `LoginPage.test.tsx` |

### 17.3.3 Deliverables

- Working registration and login
- JWT issued and verified
- Protected routes on frontend
- Auth tests passing

### 17.3.4 Verification

| Check | How |
|---|---|
| Register works | `curl -X POST /auth/register` returns 201 |
| Login works | `curl -X POST /auth/login` returns token |
| Token works | `curl -H "Authorization: Bearer ..." /auth/me` returns user |
| Duplicate email rejected | Returns 409 |
| Wrong password rejected | Returns 401 |
| Frontend login works | Manual test in browser |
| Frontend redirects | Unauthenticated user redirected to /login |
| Tests pass | `make test-backend` and `make test-frontend` |

### 17.3.5 Risks

| Risk | Mitigation |
|---|---|
| JWT misconfiguration | Test expired, wrong audience, wrong issuer |
| bcrypt slow in tests | Use lower rounds in test config |
| Token stored insecurely | Documented trade-off; no third-party scripts |
| CORS issues | Configure CORS_ORIGINS explicitly |

## 17.4 Phase 3: Core CRUD

### 17.4.1 Goal

Implement categories, expenses, budgets, and audit logging. This is
the largest phase.

### 17.4.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 3.1 | Category model and migration | `categories` table |
| 3.2 | Seed system categories | 10 categories |
| 3.3 | Category list endpoint | `GET /categories` |
| 3.4 | Category create endpoint | `POST /categories` |
| 3.5 | Category delete endpoint | `DELETE /categories/{id}` |
| 3.6 | Expense model and migration | `expenses` table |
| 3.7 | Expense create endpoint | `POST /expenses` |
| 3.8 | Expense list endpoint | `GET /expenses` |
| 3.9 | Expense get endpoint | `GET /expenses/{id}` |
| 3.10 | Expense update endpoint | `PUT /expenses/{id}` |
| 3.11 | Expense delete endpoint | `DELETE /expenses/{id}` |
| 3.12 | Budget model and migration | `budgets` table |
| 3.13 | Budget set endpoint | `PUT /budgets/{ym}` |
| 3.14 | Budget get endpoint | `GET /budgets/{ym}` |
| 3.15 | Budget delete endpoint | `DELETE /budgets/{ym}` |
| 3.16 | Audit log model and migration | `audit_logs` table |
| 3.17 | Audit writer | `app/audit/logger.py` |
| 3.18 | Integrate audit into expense service | Create, update, delete |
| 3.19 | Integrate audit into budget service | Create, update, delete |
| 3.20 | Isolation tests | `test_isolation.py` |
| 3.21 | Frontend ExpensesPage | List, filter, paginate |
| 3.22 | Frontend ExpenseForm | Create and edit modal |
| 3.23 | Frontend BudgetPage | Set, view, delete budget |
| 3.24 | Frontend CategoriesPage | List, create, delete |
| 3.25 | Frontend CRUD tests | Form and page tests |

### 17.4.3 Deliverables

- Full CRUD for expenses
- Budget management
- Category management
- Audit logging for writes
- Frontend pages for all CRUD operations
- Isolation tests passing

### 17.4.4 Verification

| Check | How |
|---|---|
| Expense CRUD works | Integration tests pass |
| Budget CRUD works | Integration tests pass |
| Category CRUD works | Integration tests pass |
| Audit log written | Check `audit_logs` table after operations |
| User isolation | User A cannot see User B's data |
| Frontend works | Manual test in browser |
| Decimal precision | Amounts stored and returned as strings |

### 17.4.5 Risks

| Risk | Mitigation |
|---|---|
| Missing user_id filter | Isolation tests in CI |
| Float instead of Decimal | Lint rule and code review |
| Audit log not written | Test audit entries after each write |
| Category deletion with expenses | RESTRICT constraint |
| Frontend form validation | Zod schemas shared with tests |

## 17.5 Phase 4: Dashboard

### 17.5.1 Goal

Implement the five dashboard visualizations and the month picker.

### 17.5.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 4.1 | Summary endpoint | `GET /dashboard/summary` |
| 4.2 | By-category endpoint | `GET /dashboard/by-category` |
| 4.3 | Trend endpoint | `GET /dashboard/trend` |
| 4.4 | Cumulative endpoint | `GET /dashboard/cumulative` |
| 4.5 | Heatmap endpoint | `GET /dashboard/heatmap` |
| 4.6 | Recent endpoint | `GET /dashboard/recent` |
| 4.7 | Dashboard aggregation tests | `test_dashboard_service.py`, `test_dashboard_api.py` |
| 4.8 | MonthContext | `context/MonthContext.tsx` |
| 4.9 | MonthPicker component | `components/layout/MonthPicker.tsx` |
| 4.10 | DashboardPage layout | `pages/DashboardPage.tsx` |
| 4.11 | KPI cards | 4 cards |
| 4.12 | CategoryPieChart | Pie chart component |
| 4.13 | MonthlyTrendChart | Bar chart component |
| 4.14 | CumulativeLineChart | Line chart with budget line |
| 4.15 | WeeklyHeatmap | Heatmap component |
| 4.16 | BudgetProgress | Progress bar component |
| 4.17 | RecentTransactions | List component |
| 4.18 | Chart component tests | Each chart has a test file |
| 4.19 | Dashboard integration tests | `test_dashboard_api.py` |

### 17.5.3 Deliverables

- Six dashboard endpoints
- Five chart components
- KPI cards
- Recent transactions list
- Month picker with global sync
- Chart tests passing

### 17.5.4 Verification

| Check | How |
|---|---|
| Summary correct | Known expenses produce known totals |
| Category breakdown | Sum of categories equals total |
| Trend includes empty months | Zero-filled months returned |
| Cumulative last point = total | Assert equality |
| Heatmap 7 days per week | Assert structure |
| Recent limit respected | Returns exactly 10 when 15 exist |
| Month switch updates all | E2E test |
| Charts render | Manual test in browser |

### 17.5.5 Risks

| Risk | Mitigation |
|---|---|
| Month boundary bug | Test Oct 31 to Nov 1 |
| Year boundary bug | Test Dec to Jan |
| Timezone issue | Use DATE, not TIMESTAMP |
| Chart library issues | Recharts is well-documented |
| Empty state missing | Test each chart with empty data |
| Heatmap alignment | Test Monday start explicitly |

## 17.6 Phase 5: Container and CI/CD

### 17.6.1 Goal

Containerize the application, set up CI/CD, and deploy to Render.

### 17.6.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 5.1 | Multi-stage Dockerfile | Node build + Python runtime |
| 5.2 | docker-compose.yml | App + PostgreSQL |
| 5.3 | Health check endpoint | `GET /health` |
| 5.4 | SQLite fallback logic | `app/database.py` |
| 5.5 | render.yaml | Render deployment config |
| 5.6 | ci.yml | PR workflow |
| 5.7 | e2e.yml | Main branch workflow |
| 5.8 | deploy.yml | Deploy workflow |
| 5.9 | Playwright setup | `e2e/` directory |
| 5.10 | happy-path.spec.ts | Complete user flow |
| 5.11 | isolation.spec.ts | User isolation |
| 5.12 | month-switch.spec.ts | Month switching |
| 5.13 | First Render deploy | Live URL |
| 5.14 | UptimeRobot setup | Ping every 10 minutes |
| 5.15 | deployment-health.md | Deployment record |

### 17.6.3 Deliverables

- Docker and Compose working
- CI runs tests on PR
- E2E runs on main
- Deploy runs after E2E
- Live URL working
- UptimeRobot pinging

### 17.6.4 Verification

| Check | How |
|---|---|
| Docker build works | `docker compose up --build` |
| Full stack runs | Open http://localhost:8000 |
| CI passes | Open a test PR |
| E2E passes | Push to main |
| Deploy works | Check Render dashboard |
| Health endpoint works | `curl /api/v1/health` |
| Cold start note in README | Read README |
| UptimeRobot active | Check UptimeRobot dashboard |

### 17.6.5 Risks

| Risk | Mitigation |
|---|---|
| Docker build slow | Multi-stage, cached layers |
| Render deploy fails | Test locally first |
| Cold start too long | UptimeRobot keeps warm |
| E2E flaky | Only test critical paths |
| CI minutes exhausted | E2E only on main |

## 17.7 Phase 6: Agent Extension Pack

### 17.7.1 Goal

Build the skills, hooks, MCP server, and subagents. Document them.

### 17.7.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 6.1 | monthly-report skill | `agent-capabilities/monthly-report/SKILL.md` |
| 6.2 | add-expense skill | `agent-capabilities/add-expense/SKILL.md` |
| 6.3 | budget-check skill | `agent-capabilities/budget-check/SKILL.md` |
| 6.4 | validate-amount hook | `agent-hooks/validate-amount.py` |
| 6.5 | validate-ownership hook | `agent-hooks/validate-ownership.py` |
| 6.6 | Hook README | `agent-hooks/README.md` |
| 6.7 | MCP server entry | `mcp-server/server.py` |
| 6.8 | MCP auth | `mcp-server/auth.py` |
| 6.9 | MCP add_expense tool | `mcp-server/tools/add_expense.py` |
| 6.10 | MCP get_budget_status tool | `mcp-server/tools/get_budget_status.py` |
| 6.11 | MCP monthly_summary tool | `mcp-server/tools/monthly_summary.py` |
| 6.12 | MCP list_expenses tool | `mcp-server/tools/list_expenses.py` |
| 6.13 | MCP README | `mcp-server/README.md` |
| 6.14 | finance-analyst subagent | `custom-agent/finance-analyst.md` |
| 6.15 | qa-reviewer subagent | `custom-agent/qa-reviewer.md` |
| 6.16 | Symlinks in `.agents/` | Discovery paths |
| 6.17 | docs/agent-extension-pack.md | Pack overview |
| 6.18 | docs/permissions.md | Permission matrix |
| 6.19 | Hook tests | `test_agent_hooks.py` |
| 6.20 | Manual MCP test | Call each tool against the backend |

### 17.7.3 Deliverables

- 3 skills
- 2 hooks
- 4 MCP tools
- 2 subagents
- Documentation
- Hook tests passing
- MCP tools verified manually

### 17.7.4 Verification

| Check | How |
|---|---|
| Skills discoverable | `ls .agents/skills/` |
| Hooks importable | `python -c "from agent_hooks.validate_amount import validate_amount"` |
| Hook tests pass | `pytest test_agent_hooks.py` |
| MCP server starts | Run with env vars |
| MCP tools work | Call each tool |
| Subagents defined | `ls .agents/agents/` |
| Permissions documented | Read docs/permissions.md |

### 17.7.5 Risks

| Risk | Mitigation |
|---|---|
| MCP server fails to start | Test locally with minimal config |
| Tool schemas too complex | Keep schemas simple |
| Hook tests fail | Pure functions, easy to test |
| Symlinks broken | Verify with `ls -la` |
| Permissions unclear | Matrix in docs/permissions.md |

## 17.8 Phase 7: Security and Ops

### 17.8.1 Goal

Run security scans, produce artifacts, and document operations.

### 17.8.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 7.1 | Run gitleaks | `security/gitleaks-report.json` |
| 7.2 | Run semgrep | `security/semgrep-report.json` |
| 7.3 | Run trivy | `security/trivy-report.json` |
| 7.4 | Run pip-audit | `security/pip-audit-report.txt` |
| 7.5 | Run npm audit | `security/npm-audit-report.txt` |
| 7.6 | Write pr-audit.md | PR review record |
| 7.7 | Write agent-security-notes.md | Agent security design |
| 7.8 | Write ai-tool-data-policy.md | AI data policy |
| 7.9 | Write ops/runbook.md | Common problems |
| 7.10 | Write ops/health-check.md | Health reference |
| 7.11 | Write ops/diagnosis.md | Worked example |
| 7.12 | Write ops/logging.md | Log format |
| 7.13 | Write ops/deployment-health.md | Deployment record |

### 17.8.3 Deliverables

- 5 scan reports
- 3 security documents
- 5 ops documents

### 17.8.4 Verification

| Check | How |
|---|---|
| All scan files exist | `ls security/` |
| No real secrets found | Read gitleaks report |
| Diagnosis is reproducible | Follow steps in diagnosis.md |
| Runbook covers common issues | Read runbook.md |
| Deployment record is accurate | Compare with live state |

### 17.8.5 Risks

| Risk | Mitigation |
|---|---|
| False positives in scans | Document accepted findings |
| Diagnosis not reproducible | Test the steps yourself |
| Runbook incomplete | Cover the 7 most common issues |
| Scan output too large | Keep only summary if needed |

## 17.9 Phase 8: Docs and Polish

### 17.9.1 Goal

Finalize documentation, add screenshots, and do end-to-end testing.

### 17.9.2 Tasks

| # | Task | Deliverable |
|---|---|---|
| 8.1 | Write README.md | Reviewer entry point |
| 8.2 | Write docs/architecture.md | Architecture doc |
| 8.3 | Write docs/api.md | API guide |
| 8.4 | Write docs/design-system.md | UI conventions |
| 8.5 | Write docs/testing-guidelines.md | Testing rules |
| 8.6 | Write docs/ai-workflow.md | AI workflow with real sessions |
| 8.7 | Capture screenshots | `screenshots/*.png` |
| 8.8 | Final test run | `make test` and `make e2e` |
| 8.9 | Final deploy | Push to main |
| 8.10 | Verify live deployment | Smoke test |
| 8.11 | Update deployment-health.md | Final record |
| 8.12 | Criteria mapping check | Verify all 14 criteria have evidence |
| 8.13 | Peer review dry run | Walk through as a reviewer would |

### 17.9.3 Deliverables

- Complete documentation
- Screenshots
- All tests passing
- Live deployment verified
- Criteria mapping complete

### 17.9.4 Verification

| Check | How |
|---|---|
| README under 500 lines | `wc -l README.md` |
| All docs present | `ls docs/` |
| Screenshots exist | `ls screenshots/` |
| All tests pass | `make test && make e2e` |
| Live URL works | Open in browser |
| Criteria mapped | Read README criteria table |

### 17.9.5 Risks

| Risk | Mitigation |
|---|---|
| Docs out of date | Update as you go, not at the end |
| Screenshots show test data | Use realistic seed data |
| Tests flaky | Run twice before final |
| Live deploy broken | Rollback to previous |

## 17.10 Milestones

| Milestone | Phase | Criteria |
|---|---|---|
| M1: Spec ready | End of Phase 1 | product-spec.md complete; issues groomed |
| M2: Auth works | End of Phase 2 | Register, login, protected routes |
| M3: MVP CRUD works | End of Phase 3 | Expenses, budgets, categories, audit |
| M4: Dashboard complete | End of Phase 4 | 5 charts, month picker |
| M5: Deployed | End of Phase 5 | Live URL, CI/CD, E2E |
| M6: Extension pack ready | End of Phase 6 | Skills, hooks, MCP, subagents |
| M7: Security and ops ready | End of Phase 7 | All artifacts present |
| M8: Peer-review ready | End of Phase 8 | Docs, screenshots, tests, deploy |

## 17.11 Risk Register

### 17.11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Render PostgreSQL expires mid-review | High | Medium | SQLite fallback (implemented) |
| Cold start confuses reviewer | Medium | Low | README note + UptimeRobot |
| pi-agent struggles with complex tasks | Medium | Medium | Smaller issues, more grooming |
| qwen3.8-27b context limit | Medium | Medium | Keep AGENTS.md short, split sessions |
| MCP server not working | Low | Medium | Test with simple tool first |
| E2E flaky | Medium | Low | Only test critical paths |
| Security scan false positives | Low | Low | Document accepted findings |
| Time overrun on dashboard | Medium | Medium | Charts are independent |
| SQLite/PostgreSQL differences | Medium | Medium | Avoid DB-specific SQL |
| Decimal handling bug | Low | High | Tests compare Decimal to Decimal |

### 17.11.2 Process Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Spec too vague | Medium | High | Grooming checklist |
| Spec too detailed | Medium | Medium | Defer to out-of-scope issues |
| AI produces wrong code | Medium | Medium | QA verification step |
| Human review skipped | Low | High | QA agent enforces |
| Issues too large | Medium | Medium | Split during grooming |
| Correction not written down | Medium | Low | Update AGENTS.md after corrections |
| Session records incomplete | Medium | Medium | Record after each session |

### 17.11.3 Scope Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Feature creep | High | High | Strict MVP scope |
| Extra chart types | Medium | Medium | 5 charts is the limit |
| Multi-currency | Low | High | Out of scope |
| Shared budgets | Low | High | Out of scope |
| Mobile app | Low | High | Out of scope |
| Dark mode | Low | Low | Out of scope |

### 17.11.4 Deployment Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Render deploy fails | Low | High | Test locally first |
| Database migration fails | Low | High | Test migrations locally |
| Cold start too long | High | Low | UptimeRobot |
| Bandwidth exceeded | Low | Low | Charts are SVG, minimal data |
| Build minutes exhausted | Low | Medium | Only deploy on main |
| Secret leaked | Low | High | gitleaks in pre-deploy |

## 17.12 Daily Workflow

Each development day follows the same pattern:

```
1. Pick the next open issue from the backlog
2. PM agent grooms it (if not already groomed)
3. SWE agent implements it
4. QA agent verifies it
5. On FAIL, SWE fixes with QA comment
6. On PASS, orchestrator closes the issue
7. Commit and push
8. CI runs
9. Update session records
```

### 17.12.1 Time Allocation

| Activity | Percentage |
|---|---|
| Writing code | 40% |
| Reviewing AI output | 20% |
| Grooming issues | 10% |
| Writing tests | 15% |
| Documentation | 10% |
| Debugging | 5% |

### 17.12.2 Session Discipline

| Rule | Reason |
|---|---|
| One issue per session | Focused context |
| Fresh session for QA | Independent verification |
| Commit after each issue | Recoverable state |
| Update docs after corrections | Prevent repeating mistakes |
| Record sessions | Evidence for Criterion 2 |

## 17.13 Development Plan Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Phase count | 8 | Balances granularity and simplicity |
| Phase order | Spec → Auth → CRUD → Dashboard → Deploy → Agent → Security → Docs | Dependencies flow naturally |
| Phase 4 and 5 parallel | Possible | Dashboard and deployment are independent |
| Estimated days | 25 | Realistic for a solo developer with AI assistance |
| Milestones | 8 | One per phase |
| Risk register | 4 categories | Technical, process, scope, deployment |
| Daily workflow | PM → SWE → QA loop | Matches the course workflow |
| Session discipline | One issue per session | Prevents context rot |
| Documentation timing | Throughout, not at the end | Avoids stale docs |
| Screenshots timing | Phase 8 | After UI is stable |
| Security scans timing | Phase 7 | After all code is written |
| Peer review dry run | Phase 8 | Catch gaps before submission |
```

---

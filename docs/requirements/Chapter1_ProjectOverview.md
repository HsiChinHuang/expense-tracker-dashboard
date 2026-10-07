# Chapter 1: Project Overview

## 1.1 Project Name and Repository

| Field | Value |
|---|---|
| Product Name | Expense Tracker & Budget Dashboard |
| Repository Name | expense-tracker-dashboard |
| License | MIT |
| Language | English (all documentation and code comments) |

The product name is intentionally descriptive. A reader should understand
what the application does from the name alone: it tracks expenses and
provides a budget dashboard.

## 1.2 One-Line Description

A full-stack personal finance application where users record expenses,
set monthly budgets, and view spending insights through an interactive
dashboard with five visualizations.

## 1.3 Target Users

- Individuals managing personal finances
- Users who want a lightweight alternative to full accounting software
- Users who want more structure than a spreadsheet
- Single-currency users (USD)
- No shared or team budgets in this version

## 1.4 Core Value

The application answers three questions for the user:

1. How much have I spent this month?
2. How much of my budget is left?
3. Where is my money going?

It answers these questions visually, not just numerically, through:

- KPI cards for quick status
- A category pie chart for distribution
- A monthly trend bar chart for comparison over time
- A cumulative spending line chart with a budget line for pace tracking
- A weekly heatmap for spending density
- A recent transactions list for immediate context

## 1.5 Final Project Criteria Mapping

The project is designed to satisfy all 14 criteria of the Final Project.

| Criterion | Evidence Location |
|---|---|
| 1. Problem Description | README.md, product-spec.md, Chapter 1 and 2 |
| 2. AI-Assisted Development Workflow | AGENTS.md, docs/ai-workflow.md, docs/process.md |
| 3. Technologies and System Architecture | docs/architecture.md, Chapter 3 and 4 |
| 4. Frontend Implementation | frontend/, frontend tests, Chapter 8 |
| 5. API Contract | openapi.yaml, Chapter 7 |
| 6. Backend Implementation | backend/, backend/tests/, Chapter 6 |
| 7. Database Integration | backend/alembic/, docs/architecture.md, Chapter 5 |
| 8. Containerization | Dockerfile, docker-compose.yml, Chapter 14 |
| 9. Integration Testing | e2e/, backend/tests/integration/, Chapter 11 |
| 10. Deployment | Live URL, render.yaml, ops/deployment-health.md |
| 11. CI/CD Pipeline | .github/workflows/ |
| 12. Agent Extension Pack | agent-capabilities/, agent-hooks/, mcp-server/, custom-agent/, docs/agent-extension-pack.md, docs/permissions.md, Chapter 9 and 10 |
| 13. Security, Audit, DevOps Hardening | security/, ops/, Chapter 12 and 13 |
| 14. Reproducibility | README.md Quick Start, Makefile, .env.example |

## 1.6 Scope Boundaries

### In Scope (MVP)

**Authentication**
- User registration with email, username, password
- Login with JWT access token (24-hour expiry)
- Password hashing with bcrypt
- Current user profile endpoint

**Expenses**
- Create, read, update, delete expenses
- Fields: amount (USD), category, date, optional note
- Filter by month and category
- Pagination (default 20 per page)

**Budgets**
- Set one monthly total budget per user per month
- Update and delete budget
- Query budget status for any month

**Categories**
- 10 system-preset categories with fixed colors
- Users can create custom categories with name and color
- Users cannot delete system categories
- Users cannot modify system categories

**Dashboard**
- Top-level month selector with global chart synchronization
- KPI cards: total spent, budget remaining, usage percentage, transaction count
- Category pie chart (top 6 + Other)
- Monthly trend bar chart (last 6 months)
- Cumulative spending line chart with budget line (turns red when over budget)
- Weekly spending heatmap (last 12 weeks)
- Recent transactions list (last 10)
- Budget progress bar with color coding

**Data Integrity**
- All user data isolated by user_id at the query level
- Amount stored as NUMERIC(12,2), handled as Decimal
- Dates stored as DATE, no timezone
- Audit log for all expense and budget create/update/delete

**Reliability**
- SQLite automatic fallback when PostgreSQL is unreachable
- Health check endpoint reports database status and fallback state

**Agent Extension Pack**
- Three skills: monthly-report, add-expense, budget-check
- Two hooks: validate-amount, validate-ownership
- MCP server with four JWT-authenticated tools
- Two subagents: finance-analyst, qa-reviewer
- Permissions matrix

**Security and Audit**
- Eight security artifacts in security/
- Five ops artifacts in ops/
- AI tool and data policy

**Deployment**
- Docker and Docker Compose
- GitHub Actions CI/CD
- Render free tier deployment
- UptimeRobot ping every 10 minutes

### Out of Scope

**Product**
- Multi-currency support
- Income tracking
- Bank API integration
- Shared or team budgets
- Mobile app
- Recurring expenses
- Receipt or image upload
- Email verification
- Password reset flow
- Dark mode
- Refresh tokens
- OAuth or social login
- Bulk delete
- Expense search by note text
- Rate limiting (documented as known limitation)
- Admin role or admin UI

**Technical**
- Kubernetes
- Managed database service (RDS)
- Private VPC or subnet configuration
- Multi-region deployment
- Custom domain with HTTPS beyond Render default
- Load balancing
- Horizontal scaling
- Real-time collaboration
- WebSocket connections
- Push notifications
- Data export (CSV, PDF)
- Internationalization (i18n)

## 1.7 Project Constraints

| Constraint | Value |
|---|---|
| Currency | USD only |
| Budget model | Monthly total per user |
| Authentication | JWT with bcrypt, no refresh token |
| Token lifetime | 24 hours |
| Password minimum length | 8 characters |
| Username format | 3-50 characters, alphanumeric and underscore |
| Expense note | Optional, max 500 characters |
| Amount precision | 2 decimal places |
| Amount maximum | 9,999,999,999.99 |
| Pagination default | 20 items |
| Pagination maximum | 100 items |
| Heatmap range | 12 weeks |
| Trend range | 6 months |
| Recent transactions | 10 items |
| Pie chart categories | Top 6 + Other |
| Documentation language | English |
| Code comments | English |

## 1.8 Success Criteria

The project is considered successful when:

1. All 14 Final Project criteria have clear evidence in the repository
2. The application is deployed and accessible via a working URL
3. All unit, integration, and end-to-end tests pass
4. A new user can register, record expenses, set a budget, and view
   the dashboard without errors
5. User data isolation is verified by automated tests
6. The SQLite fallback works when PostgreSQL is unavailable
7. The Agent Extension Pack is functional, not just documented
8. Security scan artifacts are present and reviewed
9. A peer reviewer can reproduce the setup in under 10 minutes
10. The README provides a clear 5-minute verification path
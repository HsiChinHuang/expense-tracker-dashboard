# Backlog

| ID | Title | Depends | Platform | Status |
|---|---|---|---|---|
| t0 | Repository skeleton per Chapter 16 structure | [] | #3 | closed |
| t1 | Backend skeleton (FastAPI + uv + pytest + ruff/mypy) | [t0] | #4 | closed |
| t2 | Frontend skeleton (Vite + React + TS + Tailwind + Vitest) | [t0] | #5 | closed |
| t3 | Health check endpoint GET /api/v1/health | [t1] | #6 | closed |
| t4 | Root configuration files (.env.example, Makefile, LICENSE, README) | [t1, t2] | #7 | closed |
| t5 | Database foundation - Settings, SQLAlchemy engine/session, Alembic wiring | [t1, t4] | #8 | closed |
| t6 | User model and users-table Alembic migration | [t5] | #9 | closed |
| t7 | Auth primitives - bcrypt password hashing and HS256 JWT module | [t5, t6] | #10 | closed |
| t8 | Register / login / me endpoints with auth service and get_current_user | [t7] | #11 | closed |
| t9 | Frontend auth - axios client, AuthContext, route guards, login/register pages | [t2, t8] | #12 | closed |
| t10 | Category model, Alembic revision 002, idempotent system-category seed | [t5, t6] | #13 | defined |
| t11 | Categories API - list/create/delete with system protection and access validator | [t8, t10] | #14 | defined |
| t12 | Audit foundation - audit_logs model, Alembic 003, same-transaction logger, get_client_ip | [t6, t10] | #15 | defined |
| t13 | Expenses vertical - model + Alembic 004, service, five endpoints, audit integration | [t11, t12] | #16 | defined |
| t14 | Budgets vertical - model + Alembic 005, upsert/get/delete endpoints, audit integration | [t12, t13] | #17 | defined |
| t15 | Cross-resource user-isolation and money-precision test suite | [t13, t14] | #18 | defined |
| t16 | Frontend data layer - typed api modules, queryKeys, CRUD hooks, MSW handlers | [t9, t13, t14] | #19 | defined |
| t17 | ExpensesPage + ExpenseForm modal + ToastProvider (network-error presentation) | [t16] | #20 | defined |
| t18 | BudgetPage + CategoriesPage | [t16] | #21 | defined |

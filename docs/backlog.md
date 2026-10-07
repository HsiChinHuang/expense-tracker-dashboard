# Backlog

| ID | Title | Depends | Platform | Status |
|---|---|---|---|---|
| t0 | Repository skeleton per Chapter 16 structure | [] | #3 | closed |
| t1 | Backend skeleton (FastAPI + uv + pytest + ruff/mypy) | [t0] | #4 | closed |
| t2 | Frontend skeleton (Vite + React + TS + Tailwind + Vitest) | [t0] | #5 | closed |
| t3 | Health check endpoint GET /api/v1/health | [t1] | #6 | closed |
| t4 | Root configuration files (.env.example, Makefile, LICENSE, README) | [t1, t2] | #7 | closed |
| t5 | Database foundation - Settings, SQLAlchemy engine/session, Alembic wiring | [t1, t4] | #8 | defined |
| t6 | User model and users-table Alembic migration | [t5] | #9 | defined |
| t7 | Auth primitives - bcrypt password hashing and HS256 JWT module | [t5, t6] | #10 | defined |
| t8 | Register / login / me endpoints with auth service and get_current_user | [t7] | #11 | defined |
| t9 | Frontend auth - axios client, AuthContext, route guards, login/register pages | [t2, t8] | #12 | defined |

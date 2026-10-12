# Factpack t43 (builder implement)
- Card: docs/issues/t43.md @ groom tip d1d2547 (gate1 PASS, ac_hash 4b5f875e, 5 cmds)
- RULINGS: Option A (connect-probe), A-bis (mode=driver_ok honest naming, placeholder host dpg-placeholder-a.postgres.render.com, resolution REPAIR_PG_HOST->DATABASE_URL->placeholder, no authenticated-connect requirement, REQ-CICD-070), A-ter (entry 139 amendment at merge time by orchestrator; exact leg: git diff --quiet a224be8 -- backend/app :!backend/app/database.py)
- DELTA (4 files): backend/pyproject.toml (+psycopg[binary]), backend/uv.lock, backend/app/database.py (probe inside try, except tuple BYTE-IDENTICAL (SQLAlchemyError, OSError, ImportError)), e2e probe script + e2e/psycopg-import.log
- MEASURED AT GROOM: driver-only turns t25 entries 121-124 RED (do not go that route); probe+driver = 270 passed, ruff, mypy 87, head 005
- Base REDs: ac1-ac4 rc=1 at base (analyzer: try@92/except@96 no probe inside)
- MAIN floors: 270 / 187 / lint==4 / mypy 87 / head 005 / README 8d141fb2 / workflows 4 / index 173 (131/132/133/135 pins + anchors; 139 amendment-pending DO NOT touch index)
- FORBIDDEN: docs/state/merge_test_index.json, Makefile, README, .github/workflows, frontend/

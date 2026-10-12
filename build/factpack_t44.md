# Factpack t44 (builder implement)
- Card: docs/issues/t44.md @ groom tip 112bb51 (gate1 PASS, ac_hash b6e4d660, 5 cmds)
- ROOT CAUSE: Makefile security-semgrep recipe passes --metrics off with --config auto; semgrep 1.180.0 rejects -> rc=2 at base (measured ~1s)
- REPAIRED RECIPE measured rc=0 ~53s, 32 findings (prior-run evidence; re-verify via card commands)
- RULING Option B: delta = Makefile ONLY (+handoff); Makefile blob byte-pinned post-repair; frozen files cmp vs base commit 0255037; card Constraints carry Option B text
- FORBIDDEN: security/ report regeneration/commits (t38 artifacts must stay byte-identical), merge_test_index.json, README, .github/workflows, frontend/, ops/, backend/
- MAIN floors: 270 / 187 / lint==4 / mypy 87 / head 005 / README 8d141fb2 / workflows four / index >=178 + anchors tests[16]=t2/tests[54]=t9; do NOT pin entry 139 (amendment-pending t43 A-ter); byte-pins 131/132/133/135 OK
- MERGE ORDER: t44 MUST merge BEFORE t41

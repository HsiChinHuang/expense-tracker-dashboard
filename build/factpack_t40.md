# Factpack t40 (builder implement)
- Card: docs/issues/t40.md @ groom tip c4f71ef (gate1 PASS, ac_hash 2baeb1e7, 6 cmds)
- DESIGN: register = "## Accepted Findings" section in security/agent-security-notes.md; parse-then-compare loop gate over 96 distinct measured finding ids (NOT 51 - definer re-measured across all five reports); base RED ac1-ac6 all rc=1 at 5cbe4b2; pass-after all rc=0 incl ac6 composite 11m40s
- DELTA per card (<=4 files): security docs - pr-audit record, agent-security-notes (register), ai-tool-data-policy (see card Constraints for exact file list)
- MAIN floors: 270 / 187 / lint==4 / mypy 87 / head 005 / README 8d141fb2 / workflows four / index 178 anchors t2/t9 + pins 131/132/133/135 + tests[159]; entry 139 NOW AMENDED (fe5df831, identity t27) - identity-only, do NOT re-pin
- FORBIDDEN: merge_test_index.json, Makefile, README, workflows, backend/, frontend/, e2e/
- npm ci FOREGROUND only (t43 incident); git writes cmd.exe only

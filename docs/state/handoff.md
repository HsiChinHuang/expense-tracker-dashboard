# ORCHESTRATOR HANDOFF — 2026-10-09T01:35Z (system restart pause)

Operator request: record handoff; restart system shortly.

## Exact position at pause
- **Phase**: phase_4_dashboard ACTIVE. t0–t19 ALL CLOSED. **t20 mid-build.**
- **t20 lifecycle**: groom COMPLETE + orchestrator-verified; **builder `da4c8e8c-524d-4deb-b0df-2556a1c797b6` was RUNNING at restart** (async, :medium, 180-min budget, started 01:09Z). It had NOT yet committed build output (worktree HEAD still `f89ad88` = groom handoff commit; only untracked `frontend/src/context/_probe.tsx` scratch present).
- **RESTART CONSEQUENCE: the builder run dies with the machine.** After restart: `subagent({action:"status", id:"da4c8e8c"})` → if terminal/dead, RESUME it (`action:"resume", id:"da4c8e8c", message:"restart interrupted you; check worktree state, committed vs uncommitted files, and continue the build from where you stopped"`). Resume-not-respawn is precedent (t16/t17/t18). Builder is idempotent-safe: it must `git status` the worktree first and keep/redo only its own files.

## Git / platform state at pause (all pushed)
- main = origin/main = **`06b02eb`** (chain: `46002f3` t19 CLOSED → `b273489` WAL → `d0457c2` WAL groom → `06b02eb` t20 groom handoff copy).
- t20 worktree `C:\Users\tw097\Desktop\261007_project01\worktrees\t20`, branch `issue/t20-frontend-dashboard-data-layer` @ `f89ad88` (groom commits `1221093`+`f89ad88` on `46002f3`). Deps installed (cmd.exe npm ci, 476 pkgs, win32 esbuild intact). Baseline 112/17 measured.
- Platform: #3–#22 CLOSED; **#23 open [defined]** (t20, groom done, body synced, ac_hash `sha256:7ed433bc733256fa536476ded4bc826db53821e7a5e6b63cd44a254f0cc084b2`, 6 pinned commands byte-verified in issue, 29 frozen vitest nodes, suite floor **141 = 112+29**); #24–#26 open [defined] (t21–t23). issue_map t19→22 … t23→26.
- merge_test_index: **100 entries** (t19 ac1–ac5 appended post-merge; ac6 composite excluded per precedent). merge_history: **20 entries**, regression_count 0 everywhere. WAL seq.txt = **389**.
- Suites at main: backend 230/0; frontend 112 passed/17 files; cumulative index 100/100 (last full re-scan post-t19; git-shim set re-scanned {01,04,05,12,23,24,27}).

## ⚠️ PENDING ORCHESTRATOR ACTION — legacy-index amendment (STRICT WINDOW)
`build/amend_legacy_index.cjs` is READY and dry-run-validated (dry17 rc=0 at base; dry55 rc=1 at base = correct pre-t21). It amends stored entries **#17 (t2)** drop recharts-from-forbid and **#55 (t9)** require recharts present ==2.15.4.
**EXECUTE ONLY AFTER t20 MERGE (incl. its post-merge 100-entry re-scan on the OLD entries) AND BEFORE the t21 PRE-MERGE GATE.** Command: `/mnt/d/Program/nodejs/node.exe build/amend_legacy_index.cjs` from repo root, then commit+push `docs(state): amend legacy index entries 17/55 for t21 recharts admission (review_plan W2)`. Do NOT execute earlier (would make #55 red at t20 gates while ac6 pins recharts absent).

## Resume sequence (after restart)
1. Check builder `da4c8e8c` status → resume if dead (see above). Builder deliverables: 6 new src+test files, 29 frozen titles, floor 141, tsc/lint clean, self-run 6 pinned ACs, handoff `docs/state/outputs/t20_builder_build.json` + [OK], platform #23 → [defined,built].
2. t20 verifier verify_issue (`ollama/Qwen3.8-Flash-Next-Thinking:low`, 210-min) → verify_pre_merge (`:low`, 210-min; **cumulative 100-entry RE-SCAN with fresh shim discovery + cmd.exe git shim for git-using entries + PATH restore per entry**, frontend default-reporter leg, merge-tree conflict check vs main tip).
3. t20 merge (frontend issue): `printf ... > .cm && git merge --no-ff issue/t20-frontend-dashboard-data-layer -F .cm` via cmd.exe (NEVER quoted -m with spaces); post-merge inline: 6 ACs, frontend full suite default reporter (>=141), backend 230/0, cumulative index 100 re-scan; append t20 non-composite ACs ac1–ac5 to index (ac6 composite excluded, 100→105); merge_history entry 21; #23 → [defined,merged,surveyed] + close; git mv t20.md → closed/; worktree/branch cleanup; WAL; push.
4. **THEN run the legacy-index amendment (above), commit, push.**
5. t21 (recharts 2.15.4 admission, platform #24): worktree from new main, cmd.exe npm ci, groom→build→verify→merge. t22 (DashboardPage, #25), t23 (verification, #26), then phase_4 Step 13 milestone close. Then phase_5_infra → phase_6_agent → phase_7_security_ops → phase_8_docs → final complete.md.

## Standing operator order
"keep going 直到完成整個專案，完成前不要停下" — run the whole project autonomously; do not pause for confirmation between phases. "Subagent updates above." = process notifications, continue chain.

## Environment quick-reference (Windows/WSL quirks)
- node: `/mnt/d/Program/nodejs/node.exe`; validators: `node.exe node_modules/tsx/dist/cli.mjs scripts/validate_handoff.ts <path> <role> <phase>` (from main checkout; WSL node breaks esbuild).
- git WRITE ops + all worktree git: `cmd.exe /c "git -C C:\... <op>"` (WSL git cannot open drive-letter worktrees); `</dev/null` on cmd.exe loops; NEVER pipes inside cmd.exe; commit msgs via `.cm` + `-F` (cmd.exe splits quoted -m on spaces).
- frontend tests: `cmd.exe /c "cd /d <winpath>\frontend && npm.cmd run test -- --run"` or `npx.cmd vitest run <file> --reporter=json`; worktree deps via `cmd.exe npm.cmd ci` ONLY (WSL npm ci corrupts).
- backend: `export PATH="$HOME/.local/bin:$PATH"; cd backend && uv run pytest` (venv exists in main checkout; NEVER UV_PROJECT_ENVIRONMENT).
- platform.ts: labels are TOP-LEVEL commands (`label set 23 --labels ...`); `issue get` omits body (trust definer rc=0 sync reports); body >32767 chars → compiled platform.cjs + --require preload recipe (t18/t20 precedent).
- Scratch: gitignored `build/` only; `.cm` + WAL `docs/log/2026_10_07.md` gitignored; `git add -A` banned; handoffs = repo-relative paths, strict JSON + [OK] self-proof.
- Model suffixes: `:medium` definer/builder, `:low` verifier on `ollama/Qwen3.8-Flash-Next-Thinking`. `ollama/Qwen3.6-35B-A3B` unregistered.
- Async runs die on restart; native completion notices wake the session; benign attention timers on healthy long runs (WAL note only); each verification command in its own script file, `bash <file> </dev/null`.

## Key rulings still in force
- BUILDER_COMMAND_MISMATCH: builder NEVER self-corrects pinned commands; definer amends issue body first (t18 precedent).
- t20 W3: shiftMonth/monthWindow stay exported from budget_page.tsx (extraction = red ac1 legs).
- ac6 double-absence gate (recharts+date-fns absent, tanstack ==5.56.2) is the one-door defense until the post-t20 amendment.
- Index append precedent: non-composite ACs only; composite/floor ACs stay out.
- Full frontend suite under DEFAULT reporter is a permanent pre/post-merge leg for frontend-touching issues (pinned --reporter=json legs inside AC commands are per t17/t18 precedent; the default-reporter gate lives in the merged index / orchestrator legs).
- Main-checkout dirt from artifact copies (stray `C:` junk files, modified issue files): discard/clean before merges, never commit.

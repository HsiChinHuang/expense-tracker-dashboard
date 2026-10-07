# PREFLIGHT_FAIL

Boot at: 2026-10-07T14:25Z (UTC)
Failed stage: **Stage 1 (Environment checks)**, plus a Stage 2 interpretation blocker.
Action: **HALT** this boot. Launcher will retry per `launcher.max_restart_attempts`.

---

## Blocker A — `origin/main` does not exist (Stage 1, HARD)

| Check | Expected | Actual |
|---|---|---|
| Default branch | `git symbolic-ref refs/remotes/origin/HEAD` non-empty | `fatal: ref refs/remotes/origin/HEAD is not a symbolic ref` |
| origin URL baseline | compare `docs/state/origin_url.txt` | file absent (no prior baseline) |

Evidence that the remote is **completely empty**:

- `git ls-remote --heads origin` → no refs, exit 0
- `git fetch origin` → no refs created
- GitHub API `repos/...` → `"size": 0`, `"default_branch": "main"`
- Local repo → `fatal: your current branch 'main' does not have any commits yet`

Why this is fatal for the Lifecycle, not just a warning:

- `merge.md` Step 2 does `git reset --hard origin/main`; fix branches are created
  with `git worktree add ../worktrees/... origin/main` (merge.md:168, :246).
  With no `origin/main`, every merge and every fix worktree fails.
- Builder worktrees have no base ref to branch from.

Why the Orchestrator cannot self-serve:

- No rule in `skills/orchestrator/**` authorizes the Orchestrator to create the
  initial commit or push `main`. `SKILL.md` forbids writing code; `AGENTS.md`
  rule 5 says do not guess when a rule is unclear.
- The working tree currently holds the **entire framework + user requirements**
  (876 KB `docs/`, plus `launcher/`, `extensions/`, `scripts/`, `skills/`,
  `schemas/`). Deciding what belongs in the initial commit is an owner decision,
  not a mechanical one.

Required human action (one-time bootstrap):

```bash
cd expense-tracker-dashboard
git add -A                      # .gitignore already excludes .env, node_modules, runtime state
git commit -m "chore: orchestration framework + requirements"
git push -u origin main         # credentials via GIT_ASKPASS / API_TOKEN
git fetch origin
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
```

Then record the baseline the Orchestrator compares against on every boot:

```bash
git remote get-url origin > docs/state/origin_url.txt
```

## Blocker B — Stage 2 reference integrity (needs interpretation ruling)

`preflight.md` Stage 2 says: scan all `docs/**/*.md` for `docs/...` references,
verify each static reference exists, missing → HALT.

`docs/requirements.md` (and `docs/requirements/Chapter15/17`) reference files that
do not exist:

`docs/api.md`, `docs/architecture.md`, `docs/agent-extension-pack.md`,
`docs/ai-workflow.md`, `docs/design-system.md`, `docs/permissions.md`,
`docs/process.md`, `docs/task-template.md`, `docs/testing-guidelines.md`,
`docs/team/pm.md`, `docs/team/qa-engineer.md`, `docs/team/software-engineer.md`

These are **deliverables of the project being built** (the requirements describe
documentation the finished expense-tracker must ship), not framework docs the
Orchestrator consumes. Taking Stage 2 literally means the project can never
start, because its own requirements describe files the project has not written yet.

The Stage 2 ignore list covers dynamic paths (`issues/<id>.md`,
`state/outputs/...`, `log/...`, `memory/candidates/...`) but has no rule for
"target-project deliverable paths referenced from requirements".

Proposed resolution (needs owner approval before implementation):

- Add to the Stage 2 ignore list: `docs/requirements.md`, `docs/requirements/**`,
  and any path that appears only in requirements as a *verification target*.
- Alternatively: move requirements prose out of the Stage 2 scan scope.

Framework-doc references that are legitimately pending at cold start and are
created by the Lifecycle itself — `docs/plan.md` and `docs/backlog.md` (written by
`Definer: survey`) — were **not** treated as failures.

## Non-fatal findings (WARN only, no action needed)

| Finding | Detail |
|---|---|
| `.env` permissions | `777`, expected `600` → WARN per Stage 0 Step 5 (NTFS mount, chmod has no effect) |
| `.gitattributes` | absent → WARN per Stage 3 (Stage 3 skipped: no `docs/plan.md`) |
| Toolchain runtime | `node_modules` was installed on Windows (`@esbuild/win32-x64` only). `npx tsx` cannot run from a WSL/Linux shell against `/mnt/c` (Linux ELF binaries are not executable from drvfs). All project scripts must run through the Windows toolchain (`cmd.exe /c "npx tsx ..."`), which is the intended runtime: the Launcher spawns `pi` on Windows and injects `scripts/git_askpass.cmd`. Verified working. |
| `git` identity | `user.name` / `user.email` are set in the Windows git config (`Steven.Huang`), unset in the WSL config → WARN, Windows config is the one that signs commits |
| Branch protection | API returns 404 = unprotected → passes Stage 1 ("unprotected or PR flow configured") |
| Platform API | `issue list` returns `[]`, repo metadata HTTP 200, token scopes include `repo` → ping OK |
| `automation.auto_skip_blocked` | `true` as required by the immutable-key table → OK |
| Schema migration | all state files already at current `schema_version` → no-op, no failure |

## Stage 0 outputs completed before HALT

- `.env` loaded (4 vars: `PLATFORM`, `API_TOKEN`, `REPO_ID`, `MAX_SLOTS`)
- `docs/config.yaml` loaded (`config_version: 2`)
- env override applied: `MAX_SLOTS=2` → `slots.max=2` (yaml value was 3)
- `docs/state/config_snapshot.json` written (154 keys, `sources` recorded)
- no prior snapshot → no `[CONFIG_CHANGED]`, nothing archived

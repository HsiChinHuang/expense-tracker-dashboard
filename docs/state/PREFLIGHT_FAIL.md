# PREFLIGHT_FAIL

Boot at: 2026-10-07T14:35Z (UTC) — boot following the `origin/main` bootstrap
Failed stage: **Stage 2** (+ Lifecycle Step 0 precondition, + Platform write path)
Action: **HALT**. Blocker A is resolved; B, C and D are open.

---

## Stage 1 — PASSED (was the previous HALT, now fixed)

| Check | Result |
|---|---|
| git installed / in repo / origin set | ✓ 2.43.0, `.git`, origin |
| Default branch | ✓ `refs/remotes/origin/main` |
| origin URL baseline | ✓ `docs/state/origin_url.txt` matches `git remote get-url origin` |
| `origin/main` resolvable | ✓ `df8623f`, and `main == origin/main` |
| state / log / issues dirs writable, `../worktrees` | ✓ |
| Platform API ping | ✓ repo metadata 200 |
| `PLATFORM` / `API_TOKEN` / `REPO_ID` | ✓ `github` / set / set |
| Branch protection | ✓ 404 = unprotected |
| Recovery (Stage 5) | ✓ snapshot empty, no `merge_cp.json`, prior PID 41596 dead; `seq.txt` synced |
| Pending scan (Stage 6) | ✓ `docs/issues/pending/` empty |

## Blocker A — RESOLVED (kept for audit)

Bootstrap landed as `df8623f` ("chore: orchestration framework + requirements",
142 files, requirements included), pushed to `origin/main`, `origin/HEAD` set,
`origin_url.txt` written.

## Blocker B — Stage 2 reference integrity (OPEN, needs a ruling)

Stage 2 ignores are unchanged in `df8623f`. Scan of `docs/**/*.md` still finds 12
missing static refs, all of them **deliverables of the project being built** and
named by `docs/requirements.md` as verification targets:

`ai-workflow.md` (53 hits), `permissions.md` (34), `process.md` (32),
`architecture.md` (30), `agent-extension-pack.md` (28), `testing-guidelines.md` (18),
`design-system.md` (15), `task-template.md` (14), `api.md` (12),
`team/software-engineer.md` (11), `team/qa-engineer.md` (10), `team/pm.md` (10).

Taken literally, Stage 2 can never pass: the requirements name files the project
has not written yet. Proposed fix — extend the ignore list with
`docs/requirements.md`, `docs/requirements/**`, and paths that appear only in
requirements as verification targets.

`docs/plan.md` / `docs/backlog.md` are absent too, but `Definer: survey` creates
them in Lifecycle Step 0, so they are **not** counted as failures.

## Blocker C — survey precondition: requirements headings mismatch (OPEN)

`skills/definer/details/survey.md` § Initial Input Validation requires level-2
headings `## Tech stack` and `## Core features`.

Actual `docs/requirements.md`: `### 7. Tech Stack Requirements` (level 3), and no
"Core features" heading at all. Verified mechanically —
`generate_factpack.ts phase_1_init survey` exits 0 but produces
`facts.tech_stack = null`, because `extractSection()` matches only an exact
level-2 heading.

So `Definer: survey` would emit a BLOCKER handoff on its first step, and even if it
proceeded it would have no tech stack in its factpack. Fixing this means editing
either user requirements or the Definer's validation — neither is Orchestrator
territory, so it needs an owner ruling.

## Blocker D — GitHub issue-write API returns 500 for this repo (OPEN, blocking)

Every **POST** and **DELETE** on issue-scoped endpoints returns `HTTP 500` with an
empty body. **GET** and **PATCH** work.

| Call | Result |
|---|---|
| `POST /repos/.../issues` (create) | 500 — worked at 14:28:19Z (issue #1 created), broken from ~14:55Z |
| `POST /repos/.../issues/1/comments` | 500 (3 retries + direct curl) |
| `POST /repos/.../issues/1/labels` | 500 |
| `DELETE /repos/.../labels/probe-label-x` | 500 |
| `POST /repos/.../labels` | **201 OK** |
| `PATCH /repos/.../issues/1` | **200 OK** |
| all GET | 200 OK |
| GraphQL `createIssue` | provider error (`DC77:14BE7D:…`) — not a REST-only bug |

Ruled out: rate limit (4994/5000), token scopes (`repo`, expires 2026-12-06),
Accept/media-type and `X-GitHub-Api-Version` variants, issue forms (no `.github/`
in the tree), repo config (`has_issues: true`, `disabled: false`), GitHub status
page (Issues = operational).

Why this stops the Lifecycle even after B and C are resolved: state labels are the
state machine's transport. Without label POST, issues cannot go
`defined -> groomed -> built -> verified`; Step 2 human review cannot post or read
`[RESPONSE]`; Steps 9/10 cannot create BLOCKERs; merge cannot close issues. There
is no local-label fallback in the design.

Side effect needing manual cleanup: label `probe-label-x` was created during this
diagnosis (201) and cannot be deleted (DELETE → 500).

## Non-fatal (WARN only)

- `.gitattributes` absent → Stage 3 WARN once `docs/plan.md` exists
- `.env` mode 777 vs 600 (NTFS mount; chmod ineffective)
- `node_modules` is Windows-built (`@esbuild/win32-x64`): `npx tsx` cannot run from
  a WSL/Linux shell against `/mnt/c`. Run scripts via the Windows toolchain — the
  intended runtime (Launcher spawns `pi` on Windows, injects `git_askpass.cmd`)
- git identity set in Windows config (`Steven.Huang`), unset in WSL config

## Stage 0 outputs (this boot)

`config_snapshot.json` already current (154 keys, `slots.max=2` from `MAX_SLOTS`);
no `[CONFIG_CHANGED]`; schema migration no-op.

WAL: `docs/log/2026_10_07.md` seq 10–18. Platform issue #1 body updated via PATCH
(POST unavailable).

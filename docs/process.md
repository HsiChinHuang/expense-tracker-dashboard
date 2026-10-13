# Process

This document describes the real delivery pipeline this repository runs:
a supervisor-orchestrated chain of specialized agent roles that turn
requirements into merged, verified code. It is a restatement of what
actually happens each iteration, not an idealised workflow. Related
documents: the role definitions in [team/pm.md](team/pm.md),
[team/software-engineer.md](team/software-engineer.md) and
[team/qa-engineer.md](team/qa-engineer.md), and the artifact ownership
table in [ownership.md](ownership.md).

## Roles

Five pipeline roles carry every issue from requirement to merge. Each
role has its own skill file under `skills/<role>/SKILL.md`, its own
handoff schema under `schemas/`, and a strict boundary of allowed work.

- **definer** - surveys the project, writes the plan, authors and
  grooms issue cards under `docs/issues/`. Grooming pins the
  verification commands and the ac_hash digest that every later role
  must reproduce byte-for-byte.
- **builder** - implements the acceptance criteria of one card in an
  assigned worktree, runs the card's verification commands verbatim,
  commits and pushes an `issue/<id>-<slug>` branch.
- **verifier** - independently re-runs the pinned commands, checks
  delta purity and negative controls, and records PASS or FAIL. The
  verifier never trusts a self-report.
- **orchestrator** - the long-lived coordinator. Schedules slots,
  checks gates, routes failures, and performs the transactional merge.
  It writes no code and edits no issues.
- **reviewer** - the human at the keyboard. Reviews plans, approves
  merges that touch protected surfaces, and arbitrates blockers that
  the agents must not decide alone.

The role definitions for the human job families map onto these agents:
see [team/pm.md](team/pm.md),
[team/software-engineer.md](team/software-engineer.md), and
[team/qa-engineer.md](team/qa-engineer.md).

## Orchestrator

The orchestrator owns the loop. Each iteration it:

1. Reads state labels from the platform issue tracker and
   `docs/state/` snapshots.
2. Spawns the role that the current state of each issue demands.
3. Validates every returned handoff against its schema in `schemas/`
   (for example `schemas/builder/implement.json`). A handoff that does
   not validate is rejected, never merged on trust.
4. Runs gate checks before a merge, routes failures to the retry or
   re-groom path, and appends the transaction to
   `docs/state/merge_history.json` and `merge_test_index.json`.

The handoff-schema gate is the contract that keeps the roles honest:
every role's output must conform to `schemas/<role>/<phase>.json` and
is checked by `scripts/validate_handoff.ts` before the orchestrator
accepts it.

## Lifecycle

Every issue walks one chain of states, each edge owned by exactly one
role:

defined -> groomed -> built -> verified -> closed

- (new) --definer survey--> defined
- defined --definer groom--> groomed
- groomed --builder implement--> built
- built --verifier verify_issue--> verified
- verified --orchestrator merge--> closed

Failure loops keep the chain honest: a verifier FAIL returns the issue
to the builder (fix_qa, fix_merge, or fix_regression); a card whose
acceptance criteria prove wrong goes back to the definer for
re-grooming. Issues only merge when dependencies are closed and the
gate checks pass.

## Rules

- Each role reads its own skill first and never performs another
  role's work.
- Do not edit issues outside the definer's lane; the builder does not
  approve its own work, and only the verifier records PASS.
- Verification commands are pinned at groom time and re-run verbatim;
  substituting a command is a gate failure, not a convenience.
- The delta of a card must be exactly the files its acceptance criteria
  allow; composite gates assert floor values for the whole suite so a
  card can never quietly regress the mainline.
- Merge-time growth is recorded in `docs/state/merge_test_index.json`;
  deferred work goes to the DEFERRAL_REGISTER, never into silent scope
  drift.
- Direct pushes to main are forbidden; only the orchestrator merges,
  transactionally, after the pre-merge verification.

## Agent context loading

The pipeline roles are agents, and an agent's working set is its
context. The supporting documents each role loads are fixed
(REQ-AI-022): process.md (this file), architecture.md,
design-system.md, testing-guidelines.md, api.md, openapi.yaml, and the
three team role files under `docs/team/`. A role that needs a document
not on that list reads it deliberately and says why; nothing else is
loaded by default.

Loading is on demand, not wholesale (REQ-AI-023): the agent picks its
documents by task type. A backend endpoint task pulls architecture.md
and api.md; a frontend UI task pulls design-system.md; a testing task
pulls testing-guidelines.md; PM grooming pulls the plan and the
requirements; QA verification pulls the card's pinned commands and the
criteria reports. A card that never touches the UI never loads
design-system.md, which keeps each slot's context small enough to
reason over.

The role summary at the handoff boundary is one line per role
(REQ-AI-033): the PM produces a groomed issue and no code; the SWE
produces code plus tests plus a commit and no verdict; QA produces a
PASS/FAIL comment and no code. The boundary is what the handoff schemas
enforce - a builder handoff cannot carry a PASS, and a verifier comment
cannot carry a diff.

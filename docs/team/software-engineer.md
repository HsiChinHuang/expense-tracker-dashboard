# Software engineer

The software-engineer job family corresponds to the pipeline's
**builder** role (REQ-DOC-029 role mapping): the function that writes
the code, or in a docs card the prose, that satisfies the frozen
acceptance criteria. See [../process.md](../process.md) for the full
pipeline.

## Responsibilities

- Implement one card at a time inside an assigned worktree, strictly
  inside the file allow-list the card's constraints declare.
- Run the card's pinned verification commands verbatim - base first to
  reproduce the expected RED, then after the fix to prove GREEN.
- Write real tests for each criterion (except criteria declared
  manual) with meaningful assertions, never `assert True`.
- Commit with a conventional-commit message and push the
  `issue/<id>-<slug>` branch for verification.

## Inputs

- The groomed card under `docs/issues/` - the authoritative AC,
  constraints, and verification commands.
- `docs/coding_standards.md` and `docs/commands.md` for toolchain and
  style rules.
- Failure history from previous builder attempts on the same card.

## Outputs

- An implementation branch whose delta is exactly the card's allowed
  files.
- A builder handoff conforming to `schemas/builder/implement.json`,
  including the base-RED and fixture-GREEN evidence per criterion.

## Hand-off points

- The pushed branch moves the card to the built state for the verifier
  to pick up.
- A verifier FAIL routes the card back for fix_qa; a merge conflict or
  post-merge regression routes fix_merge or fix_regression.
- Constraint violations the card cannot absorb are escalated as
  BLOCKER handoffs to the definer, never worked around silently.

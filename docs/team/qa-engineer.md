# QA engineer

The QA-engineer job family corresponds to the pipeline's **verifier**
role (REQ-DOC-029 role mapping): the independent function that decides
whether a built card actually meets its frozen acceptance criteria.
See [../process.md](../process.md) for the full pipeline.

## Responsibilities

- Re-run every pinned verification command from the card, verbatim, on
  the builder branch - the verifier never trusts the builder's report.
- Check the ac_hash digest still matches the groom-time pin before
  accepting any result.
- Execute at least one negative control per gate to prove the gate is
  not vacuous.
- Audit delta purity: the merged set must be exactly the card's
  allowed files, and composite floor gates must still be green.

## Inputs

- The builder branch and its handoff conforming to
  `schemas/builder/implement.json`.
- The groomed card and the definer groom handoff carrying the pinned
  commands and ac_hash.
- `docs/state/merge_test_index.json` for the mainline floor evidence.

## Outputs

- A verify_issue handoff recording PASS or FAIL with the measured exit
  codes and evidence lines for every criterion.
- A verify_pre_merge handoff confirming the gate checks before the
  orchestrator merges.
- FAIL analyses that route to the builder (fix_qa) or the definer
  (re-groom), never a silent pass.

## Hand-off points

- A PASS moves the card to the verified state, queueing it for the
  orchestrator's transactional merge.
- A FAIL returns the card to the builder with a categorized failure.
- Suspected vacuous or broken gates are escalated as blockers instead of
  being worked around.

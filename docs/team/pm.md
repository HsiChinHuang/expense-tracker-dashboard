# Product manager

The product-manager job family corresponds to the pipeline's **definer**
role (REQ-DOC-029 role mapping): the function that decides *what* is
built next and freezes the definition of done before any code is
written. See [../process.md](../process.md) for the full pipeline.

## Responsibilities

- Survey the repository and maintain the plan and milestone tree.
- Author issue cards from requirements, one single-purpose card per
  change, and groom each card's acceptance criteria.
- Pin the verification commands and the ac_hash digest at groom time so
  the acceptance bar cannot move under the builder's feet.
- Arbitrate card-level disputes: re-groom a card when its criteria are
  wrong, close it when they are met.

## Inputs

- `docs/requirements.md` (the user-owned requirement source).
- The current plan, backlog, and the state of closed issues.
- Reviewer feedback and blocker reports routed by the orchestrator.

## Outputs

- Issue cards under `docs/issues/` following
  [../task-template.md](../task-template.md).
- Groom handoffs conforming to `schemas/definer/groom.json`.
- Amended criteria via explicit re-groom commits, never silent edits.

## Hand-off points

- A card in the groomed state is handed to the builder through the
  orchestrator's slot scheduler.
- Re-groom requests arrive from the verifier's FAIL analysis; the
  definer's re-groom returns the card to the groomed state.
- The reviewer approves plan-level decisions before the pipeline spins
  up a new milestone.

# Document ownership

Every artifact family in this repository has one owning role and one
update trigger. The table below is the ownership map required by
REQ-DOC-063; the update triggers come from the updating rules of
REQ-DOC-062. The pipeline that applies these updates is described in
[process.md](process.md).

## Ownership table

| Artifact family | Owner | Update trigger (REQ-DOC-062) |
|---|---|---|
| Root documents (README.md, product-spec.md, AGENTS.md, CLAUDE.md, openapi.yaml, LICENSE) | reviewer-approved definer | New decision or changed entry path lands in the relevant root document at the next card that owns the surface |
| docs/ detailed documents (process.md, architecture.md, api.md, task-template.md, team/*) | definer authors, builder lands | Corrections update the relevant document; new decisions update architecture or process |
| docs/criteria/ verification evidence | verifier | A gate is re-measured or a requirement's verification mapping changes |
| security/ security artifacts | reviewer with the definer | A new audit run, a new policy decision, or a changed scan tool result |
| ops/ operations artifacts | builder under card constraint | A new deployment, runbook, or health-check procedure is decided or corrected |
| screenshots/ reviewer evidence images | reviewer | A new manual-verification pass produces fresh evidence images |

## Reading the table

- **Owner** is the role that may land the change; nobody else edits the
  family, even to fix a typo - they open a card instead.
- **Update trigger** states the event that obliges an update, per
  REQ-DOC-062: corrections update the relevant document, new decisions
  update architecture or process, new skills update the agent pack, and
  new error codes update api.md and openapi.yaml.
- The pipeline records each update through the same definer -> builder
  -> verifier chain as any other change, so an unowned edit cannot slip
  through the delta-purity gates.

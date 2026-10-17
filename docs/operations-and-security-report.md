# Operations and security report

This document is the reviewer entry point for criterion-13: one page that
summarises the operational and security story of this milestone and points at
the file that owns every fact. It restates nothing. Alert rules live in the
rule file, findings and dispositions live in the register, the incident chain
lives in its record bundle, and the tool rules live in the policy file. Where
this page states a quantity it does so as a MEASURED line naming the owning
artifact, and the acceptance fences re-extract each value from that owner
rather than trusting the prose here.

## PR audit summary

The review trail for the milestone's pull-request chain lives in
[security/pr-audit.md](security/pr-audit.md): the PR identity, the AI review
output, the issues the review found, the verification that closed them, and
the merge verdict. This page does not reproduce any of that; it records where
each part sits so a reviewer can audit it at the owner instead of trusting a
summary.

MEASURED pr_audit_sections=5 source=security/pr-audit.md

## Security scan summary

Five scanners ran against one measured commit, and each report is the single
source of truth for its own findings:
[gitleaks](security/gitleaks-report.json) for the committed-secret sweep,
[semgrep](security/semgrep-report.json) for static rules,
[trivy](security/trivy-report.json) for dependency advisories,
[pip-audit](security/pip-audit-report.txt) for the Python lock, and
[npm-audit](security/npm-audit-report.txt) for the Node lock. The anchor that
pins which commit produced the five reports together is
`docs/state/outputs/t86_scan_run.json`. Every distinct finding id the reports
emit carries a disposition row in the register
[security/agent-security-notes.md](security/agent-security-notes.md), which
owns the acceptance and limitation language; this page points at the register
and never restates a row from it.

MEASURED scan_findings_total=122 source=security/agent-security-notes.md
MEASURED scan_finding_ids=98 source=security/agent-security-notes.md
MEASURED register_rows=98 source=security/agent-security-notes.md

## Agent and extension security

The agent-facing surface is three tool trees: [extensions](extensions/),
[agent-hooks](agent-hooks/), and [mcp-server](mcp-server/). The threat model,
the control list, and the prompt-injection posture all live in
[security/agent-security-notes.md](security/agent-security-notes.md), and the
accepted findings and accepted limitations registers inside that same file own
every disposition the tooling earned. The count below is the number of source
files that make up the three trees, extracted from the trees themselves.

MEASURED extension_tools=19 source=extensions

## Operational diagnosis

The operational story - scenario, diagnosis steps, expected output, recovery
path, findings, and lessons - is owned by
[ops/diagnosis.md](ops/diagnosis.md), which was rewritten from the measured
drill rather than from assumption. The alert side lives in
[observability/alerts.yaml](observability/alerts.yaml): that file declares the
alert rules and carries the metric inventory, and this page names a rule only
by quoting the declaration, never by paraphrasing its semantics.

MEASURED diagnosis_sections=8 source=ops/diagnosis.md
MEASURED alert_rules=2 source=observability/alerts.yaml
MEASURED metric_names=4 source=observability/alerts.yaml

## AI tool and data policy

The tool inventory, data classification, data-flow rules, permitted and
forbidden uses, compliance notes, review requirements, incident-response
duties, and the recorded tracing limitation are sections of
[security/ai-tool-data-policy.md](security/ai-tool-data-policy.md). That file
is the policy of record; this page summarises its shape and never copies a
rule out of it.

MEASURED policy_sections=8 source=security/ai-tool-data-policy.md

## Incident reconstruction

The one incident record of the milestone is `2026-10-17-db-fallback-01`, kept
under the scaffold documented by
[incident-response/incidents/README.md](incident-response/incidents/README.md),
whose README owns the ID grammar and the artifact owner table. The chain walks
stage by stage, and every artifact is cited rather than pasted:

- stage:id - the record directory name is the ID, and the scaffold README
  above owns the grammar that name must match.
- stage:alert - the rule `DBFallbackActive` fired; the rule text lives only
  in [observability/alerts.yaml](observability/alerts.yaml), and the
  record's [alert.json](incident-response/incidents/2026-10-17-db-fallback-01/alert.json)
  is its extracted copy.
- stage:evidence - the measured evidence is
  [evidence.json](incident-response/incidents/2026-10-17-db-fallback-01/evidence.json);
  the raw harness bundle is described there, never reproduced here.
- stage:response - the operator actions are recorded in
  [response.json](incident-response/incidents/2026-10-17-db-fallback-01/response.json).
- stage:resolution - the closing narrative is
  [resolution.md](incident-response/incidents/2026-10-17-db-fallback-01/resolution.md).
- stage:finding - what the drill proved became findings in the register
  [security/agent-security-notes.md](security/agent-security-notes.md).
- stage:disposition - each finding's acceptance or limitation is a register
  row there, and the operational lessons sit in
  [ops/diagnosis.md](ops/diagnosis.md).

MEASURED incident_records=1 source=incident-response/incidents
MEASURED incident_artifacts=5 source=incident-response/incidents

## Known limitations

- The doc-map leg of the documentation verifier pins the root markdown set in
  a literal `DOCS_ROOT_MD` list inside
  `backend/scripts/docs_verification.py`, and this report is the single root
  document outside that pin; the pin move and the regeneration of the
  verification report are the named disposition of `t89`, the card that owns
  the README criterion row and this milestone's criteria rows, so this card
  left the pin, the generator, and its committed output
  `docs/criteria/docs_verification.md` byte-identical.
- No hosted monitoring: the alert rules exist as files only, and the
  [rule file](observability/alerts.yaml) ships no receiver configuration.
- No alert delivery to a human: the repository carries no notification
  pipeline, so a firing rule is evidence for the next operator, not a page
  bell; the operational limits are summarised in
  [ops/diagnosis.md](ops/diagnosis.md).
- No distributed tracing: the gap is recorded as an accepted limitation in
  [security/ai-tool-data-policy.md](security/ai-tool-data-policy.md).
- No CI scan job: the five scan reports come from measured local runs, not
  from a pipeline, as REQ-CICD-073 records and the same-run anchor
  `docs/state/outputs/t86_scan_run.json` evidences.
- No live production deployment: the incident record is a drill, and the
  scaffold [README](incident-response/incidents/README.md) states that the
  date inside the ID is the approved drill date.
- The register's own accepted-limitation rows are the complete list of what
  the team already refused to paper over; this page does not restate them.

MEASURED limitations_rows=13 source=security/agent-security-notes.md

## Future improvements

- `t89` moves the `DOCS_ROOT_MD` pin, regenerates the verification report,
  closes the index legs `tests[184]` and `tests[185]`, and lands the README
  row that points a reviewer at this page.
- Alert delivery and hosted monitoring become real once a receiver exists;
  until then the rule file stays the only authority and this page keeps
  pointing at it.
- The tracing gap has an accepted-limitation row in the policy and register
  and no more; closing it is a later card's work, not a claim here.
- The scan reports gain a CI job when REQ-CICD-073 is satisfied; the
  same-run anchor shows exactly what such a pipeline must reproduce.

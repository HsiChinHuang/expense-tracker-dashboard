# On-Call drill verification (t124 carrier)

This document is the measured carrier of the t124 On-Call drill half: the
recorded rehearsal that moves the On-Call Agent rubric point from 1/2 to
2/2. It is hand-authored and validated by t124's own fences (the t123
no-generator ruling stands: no generator learns this file, and
`OPS_ARTIFACTS` in `backend/scripts/docs_verification.py` stays the closed
5-name list). The pinned `| ONCALL_DRILL | <field> | <value> |` rows below
are the contract; prose is not the claim.

## Honesty rule (binding)

This drill is a DOCUMENTED REHEARSAL (the t106 precedent). This
environment has no reachable docker daemon (measured: index legs 188/192
are RED-at-tip because the daemon is unreachable), so NO container was
restarted by this card, and the carrier says so in pinned rows
(`mode = documented-rehearsal`, `live_container_operation = false`,
`docker_daemon = unreachable-at-rehearsal`). `recovery_verified` stays the
literal `false`: recovery is asserted only by the merged recovery-
verification step, never by a rehearsal document.

## Pinned drill rows

| ONCALL_DRILL | drill_id | t124-oncall-drill-01 |
| ONCALL_DRILL | claim | 2/2 |
| ONCALL_DRILL | mode | documented-rehearsal |
| ONCALL_DRILL | live_container_operation | false |
| ONCALL_DRILL | remediation_action | restart_local_compose_app |
| ONCALL_DRILL | policy_class | safe_local_remediation |
| ONCALL_DRILL | action_recordable_in_schema | true |
| ONCALL_DRILL | recovery_verified | false |
| ONCALL_DRILL | docker_daemon | unreachable-at-rehearsal |
| ONCALL_DRILL | evidence_citation | docs/criteria/scoring_map/telemetry.md, incident-response/autonomy-policy.yaml, incident-response/response.schema.json, README.md |

## What the drill rehearsed

The drill walks the full On-Call loop on one documented incident: the
alert wakes the responder contract (`incident-response/responder-task.md`),
`incident-response/collect-evidence.sh` builds the evidence bundle, the
answer is produced and validated against
`incident-response/response.schema.json` by the pinned
`incident-response/validate_response.py`, and the remediation half is
exercised as a RECORDED action: `restart_local_compose_app`, the one
`allowed_actions` id of class `safe_local_remediation` that
`incident-response/autonomy-policy.yaml` merged from t123
(`environment: local-compose-only`, docker compose grammar only). The
t124 enum extension makes that recorded action legal inside
`actions_taken`, while `restart_service` - the exact name the t81
`out_of_policy_action` mutant feeds the validator - stays OUTSIDE the enum
and stays rejected. The responder boundary is unchanged: You diagnose; a
human operates. The rehearsal never ran a container operation, never
touched production, and never claimed recovery.

## The drill's answer document

The block below is the drill's own answer, validated by
`python3 incident-response/validate_response.py --schema
incident-response/response.schema.json --answer <extracted>` (rc=0), with
`recovery_verified` the literal `false`:

```json
{
  "incident_id": "t124-oncall-drill-01",
  "summary": "documented rehearsal of the on-call loop: the bundle shows the local compose app unhealthy while the health endpoint refuses connections",
  "classification": "infrastructure",
  "severity": "low",
  "root_cause_hypothesis": "the local compose app container stopped answering its health port, the class of failure the policy-scoped local restart would clear under human operation",
  "evidence_refs": [
    "incidents/t124-oncall-drill-01/evidence/health.json",
    "incidents/t124-oncall-drill-01/evidence/manifest.json"
  ],
  "actions_taken": [
    {
      "action": "read_health",
      "justification": "the alert names the health endpoint as its trigger"
    },
    {
      "action": "restart_local_compose_app",
      "justification": "the drill records the one policy-scoped local remediation a human operated under the safe_local_remediation class"
    },
    {
      "action": "write_report",
      "justification": "the answer document itself is the recorded output of the pass"
    }
  ],
  "confidence": 0.6,
  "recovery_verified": false
}
```

## Evidence citations

- `docs/criteria/scoring_map/telemetry.md` - the On-Call section moves to
  `- Claim: 2/2` citing this carrier.
- `incident-response/autonomy-policy.yaml` - the `safe_local_remediation`
  class and the `restart_local_compose_app` id (t123's merged product).
- `incident-response/response.schema.json` - the `actions_taken[].action`
  enum gained exactly this one name; `restart_service` stays outside.
- `README.md` - criteria row 12 (On-Call Agent) reads 2/2 and cites this
  carrier alongside `docs/criteria/scoring_map/telemetry.md`.

## What this carrier does NOT claim

No live container operation happened (`live_container_operation = false`);
the docker daemon was `unreachable-at-rehearsal`; no production system was
touched; `recovery_verified` is `false` in the rows and in the answer; and
the denied trio (`restart_production`, `database_mutation`, `merge`) stays
denied by the policy's default-deny floor.

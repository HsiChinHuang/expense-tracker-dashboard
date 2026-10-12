# Factpack t38 (builder implement)
- Card: docs/issues/t38.md @ branch tip 5006798 (gate1 PASS, ac_hash 9218bde4 6 cmds)
- Delta constraint: builder touches ONLY security/semgrep-report.json + security/trivy-report.json (+ handoff); Makefile/README/workflows/backend/frontend/ops/e2e/docs-state FORBIDDEN
- Ruling: ac1 measured-rc conditional (rc=0 schema-parse; rc=2 -> uvx semgrep --config auto direct-equivalent, disclose; else exit 1). Makefile frozen (t44 repair card scheduled, merge before t41; t38 NOT gated on t44)
- Measured at groom: trivy v0.75.0 rc=0 (41 vulns+1 misconfig, 247708 bytes), semgrep 1.180.0 direct-equivalent rc=0 (32 findings), gitleaks zero-findings CR-normalized match
- fail-before base 6873ca1: all six ACs rc=1; pass-after: all six rc=0 (ac1 146s via rc=2 branch)
- MAIN floors: 270 pytest / 187 vitest / lint==4 / mypy 87 / head 005 / README 8d141fb2 / workflows 4 / index 173 anchors+5 pins

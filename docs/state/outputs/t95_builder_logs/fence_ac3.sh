set -u
test -f docs/issues/t95.md || { echo "ac3 RED: not the repo root - run the fence from the checkout root"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac3 RED: python3 missing - a skipped check proves nothing"; exit 1; }
REC=docs/state/outputs/t95_issue_close_record.json
test -s "$REC" || { echo "ac3 RED: $REC missing - nothing to check"; exit 1; }
python3 - "$REC" <<'PYEOF'
import json, os, re, sys
rec = json.load(open(sys.argv[1], encoding="utf-8"))
paths = rec.get("artifact_paths") or []
missing = [p for p in paths if not os.path.isfile(p)]
if missing:
    sys.stderr.write("ac3 RED: cited paths that do not exist in this tree: %s - a pointer to a file that is not there is the exact vacuity this fence exists to prevent\n" % missing); raise SystemExit(1)
if len(paths) < 5:
    sys.stderr.write("ac3 RED: only %d artifact paths cited - the bundle is A3 + B1a + B1b + B2 + the pointer file, so fewer than five citations means the bundle is not cited\n" % len(paths)); raise SystemExit(1)
self = "docs/state/outputs/t95_issue_close_record.json"
outside = [p for p in paths if p != self and not p.startswith("docs/issues/")]
if not outside:
    sys.stderr.write("ac3 RED: every citation is this card's own card file or the record itself - a record that cites only itself proves nothing\n"); raise SystemExit(1)
for must in ("docs/state/outputs/t92_deploy_evidence.json",
             "docs/criteria/security_ops_verification.md",
             "docs/criteria/docs_verification.md",
             "README.md",
             "ops/deployment-health.md"):
    if must not in paths:
        sys.stderr.write("ac3 RED: the bundle is not cited - %s is missing from artifact_paths\n" % must); raise SystemExit(1)
if rec.get("workflow_run_id") != 39197889153:
    sys.stderr.write("ac3 RED: workflow_run_id is not the measured 39197889153\n"); raise SystemExit(1)
mig = rec.get("register_migrations")
want = {"security_ops": {"from": 5, "to": 4}, "docs": {"from": 4, "to": 3}}
if not isinstance(mig, dict) or any(mig.get(k) != v for k, v in want.items()):
    sys.stderr.write("ac3 RED: register_migrations does not record security_ops 5->4 and docs 4->3: %s\n" % (mig,)); raise SystemExit(1)
print("ac3 evidence: %d cited paths all present, %d of them outside docs/issues and outside the record, the run id and both register migrations recorded" % (len(paths), len(outside)))
PYEOF
[ $? -eq 0 ] || { echo "ac3 RED: the citation legs failed - see the lines above"; exit 1; }
grep -qE "^DEFERRAL_REGISTER 4 DEFERRED[[:space:]]*$" docs/criteria/security_ops_verification.md || { echo "ac3 RED: the security_ops register is not at 4 DEFERRED - the B1a migration this record cites has moved; re-measure, never restate"; exit 1; }
grep -qE "^DEFERRAL_REGISTER 3 DEFERRED[[:space:]]*$" docs/criteria/docs_verification.md || { echo "ac3 RED: the docs register is not at 3 DEFERRED - the B1b migration this record cites has moved"; exit 1; }
grep -qE "^VERIFIED_ROW LIVE_DEPLOYMENT_STATE .*record=docs/state/outputs/t92_deploy_evidence[.]json[[:space:]]*$" docs/criteria/security_ops_verification.md || { echo "ac3 RED: the security_ops VERIFIED_ROW that replaced the 404 row is gone - the record would be citing a claim the tree no longer makes"; exit 1; }
grep -qE "^REQ_DEFERRAL_POINTER PASS issue=61 family=OPS artifact=ops/deployment-health[.]md" docs/criteria/req_coverage_verification.md || { echo "ac3 RED: the REQ_DEFERRAL_POINTER row for #61 is gone from the generated matrix - the pointer target this card discharges moved"; exit 1; }
python3 - <<'PYEOF' || exit 1
import json, sys
rec = json.load(open("docs/state/outputs/t92_deploy_evidence.json", encoding="utf-8"))
gap = rec.get("render_log_gap") or {}
if gap.get("captured") is not False:
    sys.stderr.write("ac3 RED: the t92 record no longer discloses render_log_gap.captured=false. This card cites t92 for the deploy evidence; if t92 changed, this card's bundle changed too - escalate for a re-groom, do not restate\n"); raise SystemExit(1)
if rec.get("workflow_run_id") != 39197889153 or rec.get("deploy_job_id") != 117884490139:
    sys.stderr.write("ac3 RED: the t92 run/job ids moved - the bundle this card cites is a different run now\n"); raise SystemExit(1)
print("ac3 evidence: the cited A3 artifact still says what the comment says it says (run 39197889153, job 117884490139, render_log_gap.captured=false)")
PYEOF
test -f docs/state/outputs/t92_evidence/deploy_run_39197889153_job_117884490139.txt || { echo "ac3 RED: the committed banked GitHub job log is missing - the A3 citation is dangling"; exit 1; }
echo "ac3 GREEN: THE BUNDLE IS CITED BY POINTER AND EVERY POINTER LANDS - five real artifacts, the run id, both register migrations re-verified against the generated reports, and the disclosed Render-log limit preserved"

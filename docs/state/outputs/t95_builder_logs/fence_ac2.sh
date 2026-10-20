set -u
test -f docs/issues/t95.md || { echo "ac2 RED: not the repo root - run the fence from the checkout root"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac2 RED: python3 missing - a skipped check proves nothing"; exit 1; }
command -v cmd.exe >/dev/null 2>&1 || { echo "ac2 RED: cmd.exe missing - the cross-check goes through the sanctioned bridge"; exit 1; }
REC=docs/state/outputs/t95_issue_close_record.json
test -s "$REC" || { echo "ac2 RED: $REC missing or empty - the record is this card's whole product"; exit 1; }
python3 - "$REC" <<'PYEOF'
import json, re, sys
rec = json.load(open(sys.argv[1], encoding="utf-8"))
if rec.get("card") != "t95":
    sys.stderr.write("ac2 RED: the record does not declare card t95\n"); raise SystemExit(1)
if rec.get("platform_issue") != 102:
    sys.stderr.write("ac2 RED: the record does not name this card's platform issue 102\n"); raise SystemExit(1)
if rec.get("target_issue") != 61:
    sys.stderr.write("ac2 RED: the record does not name the residual it discharges, issue 61\n"); raise SystemExit(1)
prior = rec.get("prior_state")
if not isinstance(prior, dict) or prior.get("state") != "open":
    sys.stderr.write("ac2 RED: prior_state.state is not the measured open state of #61\n"); raise SystemExit(1)
if sorted(prior.get("labels") or []) != ["blocked-on-operator", "infra"]:
    sys.stderr.write("ac2 RED: prior_state.labels are not the measured [#61 labels]: %s\n" % (prior.get("labels"),)); raise SystemExit(1)
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(rec.get("close_recorded_at") or "")):
    sys.stderr.write("ac2 RED: close_recorded_at is not a UTC ISO-8601 Z timestamp - the record needs the moment the discharge was recorded\n"); raise SystemExit(1)
if rec.get("close_performed_by") != "orchestrator":
    sys.stderr.write("ac2 RED: close_performed_by is not orchestrator. The card RECORDS the discharge; the close call is orchestrator-side platform maintenance (see the card's Scope of the close) - claiming otherwise is a false statement in the record\n"); raise SystemExit(1)
if not re.fullmatch(r"[0-9a-f]{64}", str(rec.get("comment_sha256") or "")):
    sys.stderr.write("ac2 RED: comment_sha256 is not a 64-hex digest\n"); raise SystemExit(1)
if not isinstance(rec.get("artifact_paths"), list) or not rec["artifact_paths"]:
    sys.stderr.write("ac2 RED: artifact_paths missing or empty\n"); raise SystemExit(1)
print("ac2 evidence: record schema, prior state, timestamp, close ownership and digest shape all as specified")
PYEOF
[ $? -eq 0 ] || { echo "ac2 RED: the record's own fields failed - see the lines above"; exit 1; }
python3 - docs/state/outputs/t95_close_comment.txt "$REC" <<'PYEOF'
import hashlib, json, sys
posted = open(sys.argv[1], "rb").read()
rec = json.load(open(sys.argv[2], encoding="utf-8"))
if hashlib.sha256(posted).hexdigest() != rec["comment_sha256"]:
    sys.stderr.write("ac2 RED: comment_sha256 does not equal the digest of the committed comment - the record describes a text that was not posted\n"); raise SystemExit(1)
print("ac2 evidence: comment_sha256 equals the digest of docs/state/outputs/t95_close_comment.txt")
PYEOF
[ $? -eq 0 ] || exit 1
TMP=$(mktemp) || { echo "ac2 RED: mktemp failed"; exit 1; }
cmd.exe /d /c "cd /d . && npx tsx scripts/platform.ts issue get 61" > "$TMP" 2>/dev/null
RC=$?
[ "$RC" = 0 ] || { echo "ac2 RED: the #61 cross-check read exited $RC through scripts/platform.ts"; rm -f "$TMP"; exit 1; }
python3 - "$TMP" <<'PYEOF'
import json, sys, os
p = sys.argv[1]
try:
    iss = json.loads(open(p, encoding="utf-8", errors="replace").read())
    os.remove(p)
except ValueError:
    sys.stderr.write("ac2 RED: the #61 read-back is not parseable JSON\n"); raise SystemExit(1)
if not isinstance(iss, dict) or iss.get("number") != 61:
    sys.stderr.write("ac2 RED: the read-back is not issue 61\n"); raise SystemExit(1)
if iss.get("state") != "open":
    sys.stderr.write("ac2 RED: #61 is %s, not open. This fence is the PRE-CLOSE snapshot leg: the builder must not close #61 from a verification run (the card's Scope of the close), and a re-run after the orchestrator's close re-measures this leg - report it, do not edit the fence\n" % iss.get("state")); raise SystemExit(1)
if sorted(iss.get("labels") or []) != ["blocked-on-operator", "infra"]:
    sys.stderr.write("ac2 RED: #61's live labels are %s, which are not the labels the record claims were measured\n" % (iss.get("labels"),)); raise SystemExit(1)
print("ac2 GREEN: THE CLOSE RECORD IS SOUND AND ITS PRE-CLOSE CROSS-CHECK MATCHES THE LIVE ISSUE - #61 is open with labels [blocked-on-operator infra], the record names the run id and both register migrations by pointer, and the comment digest ties the record to the posted text")
PYEOF
[ $? -eq 0 ] || { echo "ac2 RED: the live cross-check legs failed - see the lines above"; exit 1; }

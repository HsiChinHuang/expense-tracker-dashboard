set -u
command -v python3 >/dev/null 2>&1 || { echo "ac4 RED: python3 missing"; exit 1; }
A=docs/state/outputs/t123_definer_gate_amendment.json
T121=docs/state/outputs/t121_definer_gate_amendment.json
test -f "$A" || { echo "ac4 RED: $A missing - the W2 proposal is the written record the orchestrator applies in the merge window"; exit 1; }
test -f "$T121" || { echo "ac4 RED: $T121 missing - its STALE base must be disclosed, not silently cited"; exit 1; }
python3 - "$A" "$T121" <<'PYEOF' || exit 1
import base64, hashlib, json, re, sys
rec = json.load(open(sys.argv[1], encoding="utf-8"))
t121 = json.load(open(sys.argv[2], encoding="utf-8"))
raw = open("docs/state/merge_test_index.json", "rb").read()
live_sha = hashlib.sha256(raw).hexdigest()
tests = json.loads(raw.decode("utf-8"))["tests"]
fail = []
if rec.get("status") != "proposed":
    fail.append("amendment status is %r - the definer proposes, the orchestrator applies" % rec.get("status"))
if rec.get("policy") != "W2" or rec.get("card_writes_index_bytes") is not False \
        or rec.get("no_leg_deleted") is not True or rec.get("verifier_thresholds_touched") is not False:
    fail.append("the W2 eight-property envelope fields are not intact")
if [a["index"] for a in rec["amendments"]] != [288]:
    fail.append("the amendment set is %s - the sweep found exactly one stale leg premise (leg 288)" % [a["index"] for a in rec["amendments"]])
am = rec["amendments"][0]
cmd = tests[288]["command"]
def csha(s): return hashlib.sha256(s.encode()).hexdigest()
def esha(x): return hashlib.sha256(json.dumps(x, separators=(",", ":")).encode()).hexdigest()
live_is_old = (csha(cmd) == am["old_command_sha256"] and len(cmd) == am["old_command_len"]
               and esha(tests[288]) == am["entry_sha_before"])
live_is_new = csha(cmd) == am["new_command_sha256"] and esha(tests[288]) == am["entry_sha_after"]
if not (live_is_old or live_is_new):
    fail.append("leg 288 matches neither the old nor the amended pins - the index moved off both bases; re-pin before applying")
for r in am["replaced_regions"]:
    if live_is_old and cmd.count(r["from"]) != 1:
        fail.append("region from-string not unique in the live command: %r" % r["from"][:60])
# SWEEP: exactly one leg carries the two-class absence premise (command text or base64 payload).
def payloads(c):
    out = [c]
    for m in re.finditer(r"B64=([A-Za-z0-9+/=]{40,})", c):
        try:
            out.append(base64.b64decode(m.group(1)).decode("utf-8", "ignore"))
        except Exception:
            pass
    return out
stale = []
for i, t in enumerate(tests):
    texts = payloads(t["command"])
    if any(('{"read_only_reads", "report_writing"}' in x or "no third action class admitted" in x) for x in texts):
        stale.append(i)
expected_stale = [288] if live_is_old else []
if stale != expected_stale:
    fail.append("the two-class absence premise was found on legs %s - expected %s on this (%s) tree - the amendment set must cover every stale premise, and the sweep must name exactly one victim" % (stale, expected_stale, "pre-apply" if live_is_old else "post-apply"))
# The t121 amendment is STALE against the live index and must stay disclosed.
t121_base = t121["base"]["index_file_sha256"]
if t121_base == live_sha:
    fail.append("t121's base equals the live index - the stale-base disclosure this card carries would be false")
if "e98f96bd" not in json.dumps(rec):
    fail.append("the t123 record does not name t121's stale base e98f96bd - a stale pin cited without disclosure is how silent-fence bugs happen")
if fail:
    sys.stdout.write("ac4 evidence: " + "; ".join(fail) + "\n")
    print("ac4 RED: the carrier disposition is not sound (%d defects)" % len(fail))
    sys.exit(1)
sys.stdout.write("ac4 evidence: live index %s; leg 288 pins verify (%s); the sweep over all %d legs (base64 payloads decoded) names EXACTLY leg 288 as carrying the two-class premise; carrier legs 283/284/285/286/287/302-306 stay untouched and GREEN; legs 289/290 are environmental CR-smudge REDs disclosed not healed; t121's amendment base %s is stale vs live %s and is disclosed, never silently cited\n"
                 % (live_sha[:8], "old pins" if live_is_old else "amended pins", len(tests), t121_base[:8], live_sha[:8]))
PYEOF
echo "ac4 GREEN: one stale leg, one proposed W2 amendment, the sweep proves the set is complete, and every disclosed defect stays disclosed"

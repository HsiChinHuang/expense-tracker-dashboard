set -u
test -f docs/issues/t95.md || { echo "ac6 RED: docs/issues/t95.md missing"; exit 1; }
test -f docs/state/outputs/t95_definer_groom.json || { echo "ac6 RED: docs/state/outputs/t95_definer_groom.json missing - the groom handoff is part of the shipped surface"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac6 RED: python3 missing - a skipped check proves nothing"; exit 1; }
python3 - <<'PYEOF' || exit 1
import hashlib, json, re, sys
BT = chr(96) * 3  # built at runtime so this fence never carries a triple-backtick literal of its own
card = open("docs/issues/t95.md", "rb").read().replace(b"\r\n", b"\n").decode("utf-8")
blocks = re.findall(BT + "bash\\n(.*?)" + BT, card, re.S)
if len(blocks) != 6:
    sys.stderr.write("ac6 RED: the card carries %d bash-fenced blocks, want exactly 6\n" % len(blocks)); raise SystemExit(1)
norm = [b.replace("\r", "").strip() for b in blocks]
digest = hashlib.sha256(json.dumps(norm, separators=(",", ":")).encode("utf-8")).hexdigest()
m = re.search(r"sha256:([0-9a-f]{64})", card)
if not m:
    sys.stderr.write("ac6 RED: the card states no ac_hash literal\n"); raise SystemExit(1)
if m.group(1) != digest:
    sys.stderr.write("ac6 RED: the card states sha256:%s but the shipped fences recompute to %s - the card and the handoff must agree with the bytes\n" % (m.group(1), digest)); raise SystemExit(1)
rec = json.load(open("docs/state/outputs/t95_definer_groom.json", encoding="utf-8"))
ev = rec["evidence"]
if ev["ac_hash"] != "sha256:" + digest:
    sys.stderr.write("ac6 RED: the handoff ac_hash %s disagrees with the recomputed fence digest\n" % ev["ac_hash"]); raise SystemExit(1)
if ev["ac_count"] != 6 or sorted(ev["sections_filled"]) != ["acceptance_criteria", "context", "definition_of_done", "out_of_scope"]:
    sys.stderr.write("ac6 RED: the handoff does not record six ACs and all four filled sections\n"); raise SystemExit(1)
if sorted(ev["verification_commands"].keys()) != ["ac1", "ac2", "ac3", "ac4", "ac5", "ac6"]:
    sys.stderr.write("ac6 RED: verification_commands must cover ac1..ac6\n"); raise SystemExit(1)
if rec.get("reached_state") != "groomed":
    sys.stderr.write("ac6 RED: the handoff does not declare reached_state groomed\n"); raise SystemExit(1)
if not ev.get("base_coordination_ruling"):
    sys.stderr.write("ac6 RED: the handoff carries no base_coordination_ruling - the t94-before-t95 ordering is the premise of every pin here\n"); raise SystemExit(1)
if ev.get("index_touched_by_definer") is not False or ev.get("openapi_yaml_frozen") is not True:
    sys.stderr.write("ac6 RED: the handoff must record index_touched_by_definer false and openapi_yaml_frozen true\n"); raise SystemExit(1)
if ev.get("gate_amendments_shipped") != []:
    sys.stderr.write("ac6 RED: this card ships NO amendment record - if a leg premise moved, the fix is a re-groom amendment, not a quiet claim\n"); raise SystemExit(1)
pins = ev["as_stored_index_pins"]
idx = json.load(open("docs/state/merge_test_index.json", encoding="utf-8"))["tests"]
def esha(e):
    return hashlib.sha256(json.dumps(e, separators=(",", ":")).encode("utf-8")).hexdigest()
for k, v in pins.items():
    e = idx[int(k)]
    cs = hashlib.sha256(e["command"].encode("utf-8")).hexdigest()
    if v["command_sha256"] != cs:
        sys.stderr.write("ac6 RED: STALE PIN - the handoff pins tests[%s] command sha %s but the shipped index says %s. The orchestrator merge-window stale-check must fail here; a re-groom amendment follows, nobody guesses bytes\n" % (k, v["command_sha256"], cs)); raise SystemExit(1)
    if v["entry_sha"] != esha(e):
        sys.stderr.write("ac6 RED: STALE PIN - tests[%s] entry sha moved (%s vs %s)\n" % (k, v["entry_sha"], esha(e))); raise SystemExit(1)
    if v["command_len"] != len(e["command"]):
        sys.stderr.write("ac6 RED: STALE PIN - tests[%s] command length moved\n"); raise SystemExit(1)
sys.stdout.write("ac6 evidence: ac_hash sha256:%s recomputed from the six shipped fences; %d as-stored pins all match the shipped index; no amendment record shipped by this card\n" % (digest, len(pins)))
sys.stdout.write("ac6 GREEN: GROOM REPRODUCIBLE AND ZERO GATE MUTATION - card, handoff and fences agree byte-for-byte on the ac_hash, the as-stored pins still describe the shipped index, and this card amends no leg\n")
PYEOF

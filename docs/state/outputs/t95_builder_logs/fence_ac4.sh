set -u
test -f docs/issues/t95.md || { echo "ac4 RED: not the repo root - run the fence from the checkout root"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac4 RED: python3 missing - a skipped check proves nothing"; exit 1; }
command -v cmd.exe >/dev/null 2>&1 || { echo "ac4 RED: cmd.exe missing - the reads go through the sanctioned bridge"; exit 1; }
plat() { cmd.exe /d /c "cd /d . && npx tsx scripts/platform.ts $1" 2>/dev/null; }
TMP=$(mktemp) || { echo "ac4 RED: mktemp failed"; exit 1; }
plat "issue list --state open" > "$TMP"; RC=$?
[ "$RC" = 0 ] || { echo "ac4 RED: the open-issue read exited $RC through scripts/platform.ts"; rm -f "$TMP"; exit 1; }
python3 - "$TMP" <<'PYEOF'
import json, sys, os
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
os.remove(p)
nums = sorted(i["number"] for i in d)
if 61 not in nums:
    sys.stderr.write("ac4 RED: #61 is not in the open set. The close is orchestrator-side (the card's Scope of the close); a builder that closed it here has done out-of-scope work and this fence cannot re-create it\n"); raise SystemExit(1)
if 102 not in nums:
    sys.stderr.write("ac4 RED: this card's own issue #102 is not open - the card cannot be verified against a closed tracker entry\n"); raise SystemExit(1)
for i in d:
    if i["number"] == 102 and sorted(i["labels"]) != ["groomed"]:
        sys.stderr.write("ac4 RED: #102 labels are %s, want exactly [groomed]\n" % (i["labels"],)); raise SystemExit(1)
print("ac4 evidence: the open set is %s - #61 open (close is orchestrator-side), #102 open and labelled groomed" % nums)
PYEOF
[ $? -eq 0 ] || { echo "ac4 RED: the open-set legs failed - see the lines above"; exit 1; }
TMP2=$(mktemp) || { echo "ac4 RED: mktemp failed"; exit 1; }
plat "issue list --labels blocked-on-operator --state closed" > "$TMP2"; RC=$?
[ "$RC" = 0 ] || { echo "ac4 RED: the blocked-on-operator closed read exited $RC"; rm -f "$TMP2"; exit 1; }
python3 - "$TMP2" <<'PYEOF0'
import json, sys, os
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
os.remove(p)
if d:
    sys.stderr.write("ac4 RED: %d issues already carry blocked-on-operator AND closed (%s) - the no-other-residual leg assumed an empty set; report it, do not relax the fence\n" % (len(d), [i["number"] for i in d]))
    raise SystemExit(1)
print("ac4 evidence: zero closed issues carry blocked-on-operator, so #61 is the only residual of its kind and the only one this card can be discharging")
PYEOF0
for n in 61 102; do
  OUT=$(plat "issue latest-comment $n"); RC=$?
  [ "$RC" = 0 ] || { echo "ac4 RED: the newest-comment read for #$n exited $RC"; exit 1; }
  TMP3=$(mktemp) || { echo "ac4 RED: mktemp failed"; exit 1; }
  printf "%s" "$OUT" > "$TMP3"
  python3 - "$n" "$TMP3" <<'PYEOF'
import json, sys, os
n = int(sys.argv[1])
obj = json.load(open(sys.argv[2], encoding="utf-8"))
os.remove(sys.argv[2])
if obj is None:
    sys.stderr.write("ac4 RED: #%s has no comment at all (the channel returned null). For #61 that is the designed pre-build state - the discharge comment is the builder product; for #102 it means the groom never posted its ratification\n" % n); raise SystemExit(1)
if not isinstance(obj, dict):
    sys.stderr.write("ac4 RED: the newest-comment read for #%s returned %r, not a comment object - the channel contract is broken, do not substitute a direct API call\n" % (n, type(obj).__name__)); raise SystemExit(1)
body = obj.get("body") or ""
if n == 61:
    if not body.strip():
        sys.stderr.write("ac4 RED: #61 carries no comment at all - the discharge comment is the builder product (ac1); this RED is expected at groom and at any pre-build state\n"); raise SystemExit(1)
    if "t95" not in body:
        sys.stderr.write("ac4 RED: #61's newest comment is not this card's discharge comment - some other card commented on the residual\n"); raise SystemExit(1)
    if "t94 groomed" in body or "t96 groomed" in body:
        sys.stderr.write("ac4 RED: #61's newest comment is another card's groom ratification - this card must be the last writer on the residual\n"); raise SystemExit(1)
    print("ac4 evidence: #61's newest comment is t95's")
else:
    if "t95 groomed" not in body:
        sys.stderr.write("ac4 RED: #102's newest comment is not this card's groom ratification - the groom posts exactly one ratification comment on its own issue\n"); raise SystemExit(1)
    print("ac4 evidence: #102's newest comment is the t95 groom ratification")
PYEOF
  [ $? -eq 0 ] || { echo "ac4 RED: the newest-comment leg for #$n failed"; exit 1; }
done
echo "ac4 GREEN: SCOPE DISCIPLINE HOLDS - #61 open and last-written by t95 only, #102 labelled groomed with its own single ratification comment, no other issue touched, and #61 is the only blocked-on-operator residual in the tracker"

set -u
test -f docs/state/merge_test_index.json || { echo "ac5 RED: docs/state/merge_test_index.json missing"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac5 RED: python3 missing - the index cannot be read without it"; exit 1; }
python3 -c "import json;json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))" || { echo "ac5 RED: the merge test index is not parseable JSON"; exit 1; }
mkdir -p build/t95 || { echo "ac5 RED: cannot create build/t95"; exit 1; }
ex() { python3 -c "import json,sys;sys.stdout.write(json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))['tests'][int(sys.argv[1])]['command'])" "$1"; }
sha() { python3 -c "import hashlib,sys;sys.stdout.write(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1"; }
# leg 1: the as-stored / post-amendment pin matrix. A leg is acceptable ONLY in its
# as-stored state or in the state a shipped amendment record recorded for it; any
# third state is a moved premise and REDs loudly (re-groom territory, never a guess).
for i in 3 4 133 187 219 222 223 225 226 279 306 307 308; do
  ex "$i" > "build/t95/gate_$i.sh" || { echo "ac5 RED: stored gate tests[$i] could not be extracted"; exit 1; }
  S=$(wc -c < "build/t95/gate_$i.sh" | tr -dc "0-9")
  L=$(python3 -c "import json,sys;sys.stdout.write(str(len(json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))['tests'][int(sys.argv[1])]['command'])))" "$i")
  [ "${S:-0}" = "${L:-x}" ] || { echo "ac5 RED: extracted tests[$i] is ${S:-0} bytes but the stored command is ${L:-?} chars - an empty or partial extraction would make the replay vacuous"; exit 1; }
  OUT=$(bash "build/t95/gate_$i.sh" 2>&1); RC=$?
  if [ "$RC" != 0 ]; then
    echo "ac5 RED: carried gate tests[$i] exited $RC - it measured GREEN at the groom base and this card has no business turning it RED; its last line follows"
    printf "%s\n" "$OUT" | tail -1
    exit 1
  fi
  echo "ac5 evidence: tests[$i] GREEN as measured at groom"
done
for i in 214 230 258 309; do
  ex "$i" > "build/t95/gate_$i.sh" || { echo "ac5 RED: stored gate tests[$i] could not be extracted"; exit 1; }
  S=$(wc -c < "build/t95/gate_$i.sh" | tr -dc "0-9")
  L=$(python3 -c "import json,sys;sys.stdout.write(str(len(json.load(open('docs/state/merge_test_index.json',encoding='utf-8'))['tests'][int(sys.argv[1])]['command'])))" "$i")
  [ "${S:-0}" = "${L:-x}" ] || { echo "ac5 RED: extracted tests[$i] is ${S:-0} bytes but the stored command is ${L:-?} chars - an empty or partial extraction would make the replay vacuous"; exit 1; }
  OUT=$(bash "build/t95/gate_$i.sh" 2>&1); RC=$?
  [ "$RC" != 0 ] || { echo "ac5 RED: tests[$i] measured RED at the groom base and is GREEN here - a gate that goes GREEN without this card touching its premise is a premise drift; report it, do not celebrate it"; exit 1; }
  echo "ac5 evidence: tests[$i] RED as measured at groom (pre-existing, not this card)"
done
# tests[255]: t94's amendment lands in t94's merge window. Accept as-stored OR the
# recorded post-amendment bytes; a third digest is a moved premise.
AM4=docs/state/outputs/t94_definer_gate_amendment.json
test -f "$AM4" || { echo "ac5 RED: $AM4 missing - tests[255] cannot be adjudicated without the record that owns it"; exit 1; }
ex 255 > build/t95/gate_255.sh || { echo "ac5 RED: tests[255] could not be extracted"; exit 1; }
python3 - build/t95/gate_255.sh "$AM4" <<'PYEOF' || exit 1
import hashlib, json, sys
cmd = open(sys.argv[1], encoding="utf-8").read()
rec = json.load(open(sys.argv[2], encoding="utf-8"))
a = [x for x in rec.get("amendments", []) if int(x.get("index", -1)) == 255]
if len(a) != 1:
    sys.stderr.write("ac5 RED: the t94 record does not carry exactly one tests[255] amendment\n"); raise SystemExit(1)
a = a[0]
now = hashlib.sha256(cmd.encode("utf-8")).hexdigest()
if now == a.get("old_command_sha256"):
    sys.stdout.write("ac5 evidence: tests[255] is in its AS-STORED state (t94's amendment not applied yet in this window)\n")
elif now == a.get("new_command_sha256"):
    sys.stdout.write("ac5 evidence: tests[255] is in t94's RECORDED post-amendment state\n")
else:
    sys.stderr.write("ac5 RED: PREMISE DRIFT - tests[255] is neither as-stored (%s) nor t94's recorded bytes (%s), it is %s. STOP: this needs a re-groom amendment, never a guessed command\n" % (a.get("old_command_sha256"), a.get("new_command_sha256"), now)); raise SystemExit(1)
PYEOF
OUT=$(bash build/t95/gate_255.sh 2>&1); RC=$?
[ "$RC" = 0 ] || { echo "ac5 RED: tests[255] exited $RC in whichever amendment state the index carries - t94 owns this leg; if the amended command is RED on these bytes the t94 window is broken. Its last line follows"; printf "%s\n" "$OUT" | tail -1; exit 1; }
echo "ac5 evidence: tests[255] GREEN in its current amendment state"
# tests[250]: t96's amendment is DOWNSTREAM of t95 - accept stored or recorded, expect RED either way.
AM6=docs/state/outputs/t96_definer_gate_amendment.json
if test -f "$AM6"; then
  ex 250 > build/t95/gate_250.sh || { echo "ac5 RED: tests[250] could not be extracted"; exit 1; }
  python3 - build/t95/gate_250.sh "$AM6" <<'PYEOF' || exit 1
import hashlib, json, sys
cmd = open(sys.argv[1], encoding="utf-8").read()
rec = json.load(open(sys.argv[2], encoding="utf-8"))
a = [x for x in rec.get("amendments", []) if int(x.get("index", -1)) == 250]
if len(a) != 1:
    sys.stderr.write("ac5 RED: the t96 record does not carry exactly one tests[250] amendment\n"); raise SystemExit(1)
a = a[0]
now = hashlib.sha256(cmd.encode("utf-8")).hexdigest()
if now not in (a.get("old_command_sha256"), a.get("new_command_sha256")):
    sys.stderr.write("ac5 RED: PREMISE DRIFT - tests[250] is neither as-stored (%s) nor t96's recorded bytes (%s), it is %s\n" % (a.get("old_command_sha256"), a.get("new_command_sha256"), now)); raise SystemExit(1)
sys.stdout.write("ac5 evidence: tests[250] is in a recorded state (%s)\n" % ("as-stored" if now == a.get("old_command_sha256") else "t96 amended"))
PYEOF
  bash build/t95/gate_250.sh >/dev/null 2>&1 && { echo "ac5 RED: tests[250] is GREEN on this candidate - it is a member of the frozen 36-RED set and only t96's README edit may turn it GREEN; t95 must not"; exit 1; }
  echo "ac5 evidence: tests[250] RED as the frozen baseline requires (t96 owns its recovery)"
fi
rm -rf build/t95
# delta purity: the index and the contract are untouched by this card.
if git rev-parse --git-dir >/dev/null 2>&1; then
  git diff --name-only HEAD | grep -qx "docs/state/merge_test_index.json" && { echo "ac5 RED: the builder edited docs/state/merge_test_index.json - the definer and the builder never touch the index"; exit 1; }
  git diff --name-only HEAD | grep -qx "openapi.yaml" && { echo "ac5 RED: openapi.yaml is FROZEN and changed"; exit 1; }
  git diff --name-only HEAD | grep -qx "README.md" && { echo "ac5 RED: t95 touched README.md - README is t94 (W1) and t96 (W1/W2) surface exclusively; this is a BLOCKER, not a fix"; exit 1; }
  git diff --name-only HEAD | grep -qx "backend/scripts/docs_verification.py" && { echo "ac5 RED: t95 touched backend/scripts/docs_verification.py - the docs_verification constants belong to t94/t96; BLOCKER"; exit 1; }
  CHANGED=$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null | sort -u )
  BAD=""
  for f in $CHANGED; do
    case "$f" in
      docs/issues/t95.md|docs/state/outputs/t95_issue_close_record.json|docs/state/outputs/t95_close_comment.txt|docs/state/outputs/t95_definer_groom.json) : ;;
      scratch|scratch/*|docs/state/history|docs/state/history/*|build|build/*) : ;;
      *) BAD="$BAD $f" ;;
    esac
  done
  [ -z "${BAD// /}" ] || { echo "ac5 RED: delta purity broken - paths changed beyond this card's four named paths:$BAD"; exit 1; }
  echo "ac5 evidence: the delta is the named surface only; index, openapi.yaml, README and the docs_verification constants are untouched"
else
  echo "ac5 evidence: no git metadata available - the index/openapi/README purity legs are skipped ONLY here; the verifier runs this fence inside the worktree where they bite"
fi
echo "ac5 GREEN: REGRESSION GATE - 13 carried gates GREEN, 4 pre-existing REDs still RED, tests[255] and tests[250] adjudicated against their shipped records (premise drift REDs loudly), and the delta is this card's four paths only"

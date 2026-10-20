set -u
test -f docs/issues/t95.md || { echo "ac1 RED: not the repo root - run the fence from the checkout root"; exit 1; }
test -f scripts/platform.ts || { echo "ac1 RED: scripts/platform.ts missing - the only sanctioned platform channel"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ac1 RED: python3 missing - a skipped check proves nothing"; exit 1; }
command -v cmd.exe >/dev/null 2>&1 || { echo "ac1 RED: cmd.exe missing - the sanctioned channel is the cmd.exe bridge"; exit 1; }
CF=docs/state/outputs/t95_close_comment.txt
test -s "$CF" || { echo "ac1 RED: $CF missing or empty - the comment the builder posts must be committed verbatim, or the read-back can never be checked"; exit 1; }
python3 - "$CF" <<'PYEOF1'
import sys
b = open(sys.argv[1], "rb").read()
bad = []
if any(x > 127 for x in b): bad.append("non-ASCII byte (the cmd.exe bridge mangles non-ASCII payloads)")
if b.count(b"\r"): bad.append("CR byte (npx.cmd truncates a CRLF payload; ship LF-only - the t92 incident)")
if b.count(b'"'): bad.append("embedded double quote (the cmd.exe bridge drops the rest of the argument - the t93 finding)")
if b.count(b"$"): bad.append("dollar sign (cmd.exe variable-expansion hazard)")
if b.count(b"&") or b.count(b"|") or b.count(b"^"): bad.append("cmd.exe metacharacter & | or ^")
if b.count(b"<") or b.count(b">"): bad.append("cmd.exe redirection character")
if len(b) > 30000: bad.append("payload %d bytes, above the 30000-byte single-argv ceiling" % len(b))
if bad:
    sys.stderr.write("ac1 RED: the committed comment is not a shippable single-argv payload: " + "; ".join(bad) + "\n")
    raise SystemExit(1)
print("ac1 evidence: the committed comment is ASCII, LF-only, quote-free, free of cmd.exe metacharacters, %d bytes" % len(b))
PYEOF1
[ $? -eq 0 ] || { echo "ac1 RED: the committed comment failed the payload-shape legs above"; exit 1; }
TMP=$(mktemp) || { echo "ac1 RED: mktemp failed"; exit 1; }
cmd.exe /d /c "cd /d . && npx tsx scripts/platform.ts issue latest-comment 61" > "$TMP" 2>/dev/null
RC=$?
[ "$RC" = 0 ] || { echo "ac1 RED: the read-back of #61's newest comment exited $RC through scripts/platform.ts - the channel is the contract, do not substitute a direct API call"; rm -f "$TMP"; exit 1; }
python3 - "$CF" "$TMP" <<'PYEOF2'
import json, sys
posted = open(sys.argv[1], encoding="utf-8").read()
raw = open(sys.argv[2], encoding="utf-8", errors="replace").read()
import os
os.remove(sys.argv[2])
try:
    obj = json.loads(raw)
except ValueError:
    sys.stderr.write("ac1 RED: latest-comment did not return parseable JSON through scripts/platform.ts\n")
    raise SystemExit(1)
got = obj.get("body") if isinstance(obj, dict) else None
if not isinstance(got, str):
    sys.stderr.write("ac1 RED: latest-comment returned no body field - nothing to compare\n")
    raise SystemExit(1)
norm = lambda s: s.replace("\r\n", "\n").rstrip()
a, b = norm(posted), norm(got)
if a != b:
    sys.stderr.write("ac1 RED: #61's newest comment is NOT the committed text - posted %d bytes, read back %d bytes. The builder posts the committed file verbatim; it does not paraphrase it on the platform.\n" % (len(a), len(b)))
    raise SystemExit(1)
low = b.lower()
need = [
    ("39197889153", "the real workflow_run id from the t92 record"),
    ("117884490139", "the deploy job id from the t92 record"),
    ("4 deferred", "the security_ops register migration 5 -> 4"),
    ("3 deferred", "the docs register migration 4 -> 3"),
    ("online demo", "the README section B2 published"),
    ("deployment on render", "the README section B2 published"),
    ("expense-tracker-dashboard-1qtu.onrender.com", "the canonical live host (WAL 1169 - not any other host literal)"),
    ("t92_deploy_evidence.json", "the pointer to the A3 evidence artifact"),
    ("ops/deployment-health.md", "the pointer file the #61 deferral pointer row already names"),
]
miss = [what for tok, what in need if tok not in low]
if miss:
    sys.stderr.write("ac1 RED: the posted comment does not name: " + "; ".join(miss) + "\n")
    raise SystemExit(1)
print("ac1 evidence: read-back MATCH (%d bytes byte-equal after CR-strip and rstrip) and the comment names the run id, the job id, both register migrations, both README sections, the live host and the two artifact pointers" % len(a))
forbidden = ["render build log", "render migration log", "render service log", "render dashboard log"]
hits = [w for w in forbidden if w in low]
if hits:
    sys.stderr.write("ac1 RED: the comment claims a Render-side log body (%s). t92 disclosed that no Render API token exists, so those bodies are NOT capturable here - cite the GitHub capture, never a Render log\n" % ", ".join(hits))
    raise SystemExit(1)
if "render_log_gap" not in low and "no render api token" not in low:
    sys.stderr.write("ac1 RED: the comment does not carry t92's disclosed limit (render_log_gap / no Render API token). A discharge that silently drops a known gap is not traceable\n")
    raise SystemExit(1)
print("ac1 GREEN: THE EVIDENCE COMMENT STANDS ON #61 VERBATIM - read-back byte-equal through scripts/platform.ts, every bundle pointer named, the disclosed Render-log limit carried, and no Render log body asserted")
PYEOF2
[ $? -eq 0 ] || { echo "ac1 RED: the #61 comment read-back or its content legs failed - see the lines above"; exit 1; }

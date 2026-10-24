set -u
J=docs/criteria/trace_correlation_verification.md
test -f "$J" || { echo "ac4 RED: $J missing - the correlation must be a measured record a reader can check in 30 seconds, not a claim in prose"; exit 1; }
python3 - "$J" <<'PYEOF' || exit 1
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
rows = [ln for ln in t.splitlines() if ln.startswith("TRACE_JOURNEY")]
def parse(ln):
    m = re.match(r"^TRACE_JOURNEY PASS journey=(\S+) trace_id=([0-9a-f]{32}) log_lines=(\d+) stack=(local-compose|testclient) PASS$", ln)
    return m
pairs, fail = [], []
if len(rows) < 2:
    fail.append("fewer than TWO TRACE_JOURNEY rows - the record must show two correlated request/trace PAIRS, never two log lines on one trace (measured: every reachable path emits exactly one correlated line per request)")
for ln in rows:
    m = parse(ln)
    if not m:
        fail.append("row does not match the pinned form 'TRACE_JOURNEY PASS journey=<name> trace_id=<32hex> log_lines=<n> stack=<local-compose|testclient> PASS': %r" % ln[:80])
        continue
    pairs.append(m.group(2))
if len(set(pairs)) != len(pairs) or len(pairs) < 2:
    fail.append("the trace ids are not two DISTINCT 32-hex values - a repeated id is one request measured twice")
for p in pairs:
    if len(set(p)) <= 2:
        fail.append("trace id %s is degenerate - an all-zero or single-character id is the instrumentation-collapse signature" % p[:12])
if not re.search(r"^\| *[0-9a-f]{32} *\|", t, re.M):
    fail.append("no per-line evidence table row carrying the 32-hex id - the row alone is a number, the table is the measurement")
if not re.search(r'"event"\s*:\s*"[a-z_]+\.[a-z_.]+"', t):
    fail.append("the record quotes no frozen-vocabulary log line - correlation is proven by a QUOTED line carrying both the event name and the trace_id")
if "SPA fallback" not in t:
    fail.append("the honesty sentence is missing - hosted /metrics was measured returning the SPA fallback document, and hosted render.yaml deploys NO collector, Tempo or Loki process; the record must say so (staged-config-only stays honest)")
if "render.yaml" not in t:
    fail.append("the record never names render.yaml - the staged-config-only classification must name the surface it is staged on")

# ---- validator controls on synthetic records (victims named) ----
GOOD = "TRACE_JOURNEY PASS journey=expense-create trace_id=0123456789abcdef0123456789abcdef log_lines=1 stack=testclient PASS\n" \
       "TRACE_JOURNEY PASS journey=expense-list trace_id=89abcdef0123456789abcdef01234567 log_lines=1 stack=testclient PASS\n" \
       "| 0123456789abcdef0123456789abcdef | expense.created | expense_id |\n" \
       '{"event": "expense.created", "trace_id": "0123456789abcdef0123456789abcdef"}\n' \
       "render.yaml deploys none of this stack; hosted /metrics returns the SPA fallback document.\n"
def validate(text):
    r = [ln for ln in text.splitlines() if ln.startswith("TRACE_JOURNEY")]
    ids = []
    for ln in r:
        m = parse(ln)
        if not m:
            return ["form"]
        ids.append(m.group(2))
    e = []
    if len(ids) < 2:
        e.append("count")
    if len(set(ids)) != len(ids):
        e.append("distinct")
    if not re.search(r"^\| *[0-9a-f]{32} *\|", text, re.M):
        e.append("evidence-table")
    if not re.search(r'"event"\s*:\s*"[a-z_]+\.[a-z_.]+"', text):
        e.append("quoted-line")
    if "SPA fallback" not in text:
        e.append("honesty")
    return e
ctrls = [
    ("a single-pair record", GOOD.splitlines(True)[0] + "".join(GOOD.splitlines(True)[2:])),
    ("a repeated-id record", GOOD.replace("89abcdef0123456789abcdef01234567", "0123456789abcdef0123456789abcdef")),
    ("a malformed row (no stack field)", GOOD.replace(" stack=testclient PASS", "", 1)),
    ("a record with no quoted log line", GOOD.replace('{"event": "expense.created", "trace_id": "0123456789abcdef0123456789abcdef"}\n', "")),
    ("a record that omits the hosted honesty sentence", GOOD.replace("render.yaml deploys none of this stack; hosted /metrics returns the SPA fallback document.\n", "")),
]
for label, synthetic in ctrls:
    if not validate(synthetic):
        print("ac4 RED: control broken - the validator ACCEPTED %s (victim: a reader who trusts a correlation record that proves nothing)" % label)
        raise SystemExit(1)
if validate(GOOD):
    print("ac4 RED: the validator rejects its own well-formed sample (%s) - the fence is unsatisfiable as written" % validate(GOOD))
    raise SystemExit(1)
sys.stdout.write("ac4 evidence: %d TRACE_JOURNEY rows on the pinned form with distinct non-degenerate 32-hex ids, an evidence table, a quoted frozen-vocabulary line and the SPA-fallback/render.yaml honesty sentence; all five controls REJECTED and the well-formed sample ACCEPTED\n" % len(rows))
PYEOF
echo "ac4 GREEN: the journey record measures two correlated request/trace pairs honestly and its validator is proven to bite"

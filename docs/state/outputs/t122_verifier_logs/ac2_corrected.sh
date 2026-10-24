set -u
L=ops/logging.md
test -f "$L" || { echo "ac2 RED: ops/logging.md missing"; exit 1; }
grep -rE 'trace_id' backend/app || { echo "ac2 RED: no app module emits a trace_id field - the vocabulary cannot gain a field nobody writes"; exit 1; }
python3 - "$L" <<'PYEOF' || exit 1
import re, sys
path = sys.argv[1]
t = open(path, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
sec = re.search(r"^## Events\n(.*?)(?=^## |\Z)", t, re.M | re.S)
if not sec:
    print("ac2 RED: no '## Events' section in ops/logging.md"); raise SystemExit(1)
body = sec.group(1)
rows = re.findall(r"^\| ([a-z_]+\.[a-z_.]+) \| (DEBUG|INFO|WARNING|ERROR|CRITICAL) \| (.+) \|$", body, re.M)
WANT = ["auth.login","auth.login_failed","auth.register","budget.created","budget.deleted",
        "budget.updated","category.created","category.deleted","db.connected","db.connection_restored",
        "db.error","db.fallback_initialized","db.fallback_triggered","expense.created","expense.deleted",
        "expense.updated","unhandled.error"]
fail = []
if len(rows) != 17:
    fail.append("the event table has %d rows, not the frozen 17 - the field is ADDED, the vocabulary is not extended" % len(rows))
names = sorted(n for n, _, _ in rows)
if names != sorted(WANT):
    fail.append("the event set drifted (a rename is a new event): %s" % ",".join(names))
fmt = re.search(r"^## Format\n(.*?)(?=^## |\Z)", t, re.M | re.S)
if not fmt or '"trace_id"' not in fmt.group(1):
    fail.append("the Format example does not carry a \"trace_id\" key - every line is one JSON object, so the field belongs in the format, not in an event row")
if not re.search(r"trace_id", body):
    fail.append("the events section never mentions trace_id - a reader of the vocabulary must learn the field is present on every correlated line")
if re.search(r"^\| *trace(_|\.)?id *\|", body, re.M):
    fail.append("trace_id was added as an EVENT row - it is a field, not an event; the count must stay 17")

# ---- negative controls on synthetic text (victims named; no product byte touched) ----
def validate(text):
    s = re.search(r"^## Events\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    b = s.group(1) if s else ""
    r = re.findall(r"^\| ([a-z_]+\.[a-z_.]+) \| (DEBUG|INFO|WARNING|ERROR|CRITICAL) \| (.+) \|$", b, re.M)
    f = []
    if len(r) != 17:
        f.append("count")
    if sorted(n for n, _, _ in r) != sorted(WANT):
        f.append("names")
    fm = re.search(r"^## Format\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not fm or '"trace_id"' not in fm.group(1):
        f.append("no_trace_id_field")
    return f
head = t[:t.index("## Events")]
tail = t[t.index("## Events"):]
ctrl = []
ctrl.append(("an 18-event table", tail.replace("| unhandled.error | ERROR | error_type |",
              "| unhandled.error | ERROR | error_type |\n| trace.exported | INFO | trace_id |", 1)))
ctrl.append(("a doc without the trace_id field", re.sub(r'"trace_id"[^\n]*', "", t)))
ctrl.append(("a renamed event", tail.replace("| db.connected |", "| db.connection_opened |", 1)))
for label, synthetic in ctrl:
    if not validate(synthetic):
        print("ac2 RED: control broken - the validator ACCEPTED %s, so the vocabulary fence proves nothing (victim: every future reader of ops/logging.md)" % label)
        raise SystemExit(1)
if fail:
    sys.stdout.write("ac2 evidence: " + "; ".join(fail) + "\n")
    print("ac2 RED: the vocabulary did not gain the field cleanly (%d defects)" % len(fail))
    raise SystemExit(1)
sys.stdout.write("ac2 evidence: 17 event rows survive byte-identical in name set; trace_id is documented in Format and Events; all three controls (18-event table, no-trace_id doc, renamed event) were REJECTED\n")
PYEOF
echo "ac2 GREEN: the seventeen-event vocabulary keeps seventeen events and gains the trace_id field, with the three vocabulary controls proven"

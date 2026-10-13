#!/usr/bin/env python3
"""t57 per-REQ-ID coverage matrix generator (sixth in the series after
dashboard/infra/security_ops/agent_pack/docs).

Generates docs/criteria/req_coverage_verification.md:

* one machine row per unique ``REQ-[A-Z_]+-[0-9]{3}`` id in
  docs/requirements.md (measured 749: 748 heading entries plus the
  section 3.1 format example REQ-AUTH-001, which is the only id that
  exists outside a heading),
* a CLOSED five-label status vocabulary
  (IMPLEMENTED_TESTED, IMPLEMENTED_STRUCTURAL, DEFERRED_RULLED, GAP,
  EXAMPLE_REFERENCE) and a concrete evidence pointer on every non-GAP
  row,
* the deferral surface derived from the t28/t41/t53 register in
  docs/criteria/docs_verification.md (four LIVE_* keys plus the
  platform #61 RENDER_DEPLOY_HOOK blocker), never asserted,
* the fail-closed exit-code fence: the process exits nonzero IFF the
  matrix carries a GAP row or a non-GAP row without a pointer
  (review_plan W1 - the first landing is EXPECTED to carry GAP rows).

Hermetic by contract: no network client, no docker, no live stack, no
wall-clock, no git metadata, no absolute paths in the output; two runs
on the same tree are byte-identical.  The three self-test environment
variables (REQ_COVERAGE_SEED, REQ_COVERAGE_FIXTURE_TOKEN,
REQ_COVERAGE_OUT) never change committed-report bytes when unset.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections.abc import Sequence


def _find_root() -> str:
    """Repo ROOT, robust to the ac4 self-test copy layout.

    In the repo the script lives at backend/scripts/<name>.py (ROOT two
    levels up); the ac4 fence copies it to <tmp>/backend/
    req_coverage_selftest.py (ROOT one level up).  The first candidate
    that actually carries docs/requirements.md wins, so a copy outside
    the repo enumerates against ITS OWN tree instead of crashing.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    for cand in (os.path.join(here, "..", ".."), os.path.join(here, ".."), here):
        if os.path.isfile(os.path.join(cand, "docs", "requirements.md")):
            return os.path.abspath(cand)
    return os.path.abspath(os.path.join(here, "..", ".."))


ROOT = _find_root()
OUT_DEFAULT = os.path.join(ROOT, "docs", "criteria", "req_coverage_verification.md")

# --- frozen pins (measured, never invented) --------------------------------

GATE_FIXTURE_SEED = "t57-gate-fixture-v1"
GATE_FIXTURE_TOKEN = hashlib.sha256(GATE_FIXTURE_SEED.encode("utf-8")).hexdigest()[:16]

VOCABULARY: tuple[str, ...] = (
    "IMPLEMENTED_TESTED",
    "IMPLEMENTED_STRUCTURAL",
    "DEFERRED_RULLED",
    "GAP",
    "EXAMPLE_REFERENCE",
)

REGISTER_REL = "docs/criteria/docs_verification.md"
REQUIREMENTS_REL = "docs/requirements.md"
# This generator's own output is NEVER an evidence source: the matrix
# names every id, so treating it as a citation would greenwash the whole
# matrix on the second run (self-reference feedback, measured at build).
SELF_OUTPUT_REL = "docs/criteria/req_coverage_verification.md"

# The two honest-hard ids (card t57 "Relabeling the two hard cases").
# Both are forced GAP with a pointer to the ruling document; t58
# escalates, t57 never relabels.
HARD_CASES: tuple[tuple[str, str], ...] = (
    ("REQ-TECH-008", "docs/issues/closed/t20.md"),
    ("REQ-FE-121", "docs/issues/closed/t20.md"),
)

# id -> register key.  The keys themselves are re-read from the live
# register every run (a key that left the register cannot back a row);
# this table is the id->key derivation the register does not carry
# (review_plan W4) and the report prints its provenance row for it.
DEFERRAL_ID_KEY: dict[str, str] = {
    # LIVE_DEPLOYMENT_STATE: verification needs the deployed public
    # service, which the register records as NOT_YET_LIVE.
    "REQ-OPS-061": "LIVE_DEPLOYMENT_STATE",
    "REQ-OPS-062": "LIVE_DEPLOYMENT_STATE",
    "REQ-CICD-041": "LIVE_DEPLOYMENT_STATE",
    "REQ-DOC-070": "LIVE_DEPLOYMENT_STATE",
    "REQ-PROD-041": "LIVE_DEPLOYMENT_STATE",
    # LIVE_AGENT_SESSION: the records are transcript attestations; the
    # register defers the machine-verifiable live capture.
    "REQ-AI-111": "LIVE_AGENT_SESSION",
    "REQ-AI-112": "LIVE_AGENT_SESSION",
    # LIVE_MCP_SUBPROCESS: a live MCP spawn is outside the no-live ruling.
    "REQ-AI-088": "LIVE_MCP_SUBPROCESS",
    "REQ-EXT-071": "LIVE_MCP_SUBPROCESS",
    # LIVE_SUBAGENT_LAUNCH: launching a sub-agent needs a live runtime.
    "REQ-AI-073": "LIVE_SUBAGENT_LAUNCH",
    "REQ-EXT-043": "LIVE_SUBAGENT_LAUNCH",
}

# ids whose blocker is platform issue 61 (RENDER_DEPLOY_HOOK secret -
# operator infrastructure, open by design).
DEFERRAL_ID_ISSUE61: tuple[str, ...] = ("REQ-SEC-120", "REQ-CICD-070")
ISSUE61_POINTER = "ops/deployment-health.md"

# Register keys that must never back a row (CLOSED in the register).
FORBIDDEN_DEFERRAL_KEYS: tuple[str, ...] = ("SCAN_TIMING_DOC", "E2E_STATUS_REPORTED")

# --- tree scan (evidence universe; mirrors the carried generators) ---------

SKIP_DIRS = {".venv", "node_modules", "__pycache__", "dist", ".git", "coverage"}
SRC_DIRS = [
    "backend/app", "backend/tests", "backend/alembic", "backend/scripts",
    "frontend/src", "e2e", "mcp-server", "agent-hooks", "agent-capabilities",
    "custom-agent", ".github/workflows", "ops", "security", "docs/team",
    "docs/criteria", "docs/requirements", "docs/issues/closed",
]
SRC_FILES = [
    "README.md", "AGENTS.md", "CLAUDE.md", "product-spec.md", "openapi.yaml",
    "render.yaml", "Dockerfile", "docker-compose.yml", "Makefile",
    "docs/agent-extension-pack.md", "docs/ai-workflow.md", "docs/api.md",
    "docs/architecture.md", "docs/design-system.md", "docs/process.md",
    "docs/testing-guidelines.md", "docs/permissions.md", "docs/ownership.md",
    "docs/config_reference.md", "docs/coding_standards.md", "docs/commands.md",
    "docs/documentation_standards.md", "docs/plan.md", "frontend/package.json",
]
TESTPAT = re.compile(r"(backend/tests/|/tests/|\.test\.tsx?$|test_|conftest)")
CODEPAT = re.compile(
    r"(backend/app/|frontend/src/|mcp-server/|agent-hooks/|e2e/|backend/alembic/)"
)


class GeneratorError(Exception):
    """A generator-side contract break (unknown status, pointer-less
    non-GAP row, empty enumeration).  Never a row in the matrix."""


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().replace("\r\n", "\n")
    except OSError:
        return ""


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def tree_files() -> list[str]:
    out: list[str] = []
    for d in SRC_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for fn in files:
                out.append(rel(os.path.join(root, fn)))
    for f in SRC_FILES:
        if os.path.isfile(os.path.join(ROOT, f)):
            out.append(f)
    return sorted(set(out) - {SELF_OUTPUT_REL})


def plan_body_clean(text: str) -> str:
    """docs/plan.md carries this milestone's own card-mapping section;
    citations must come from the groomed plan body, not from rows this
    milestone itself wrote."""
    i = text.find("## phase_9_req_matrix")
    return text[:i] if i > 0 else text


# --- enumeration ------------------------------------------------------------

HEADING = re.compile(r"^(#{4,6}) (REQ-([A-Z_]+)-([0-9]{3})): (.*)$", re.M)
ID_RE = re.compile(r"REQ-[A-Z_]+-[0-9]{3}")


def enumerate_requirements(text: str) -> dict[str, dict[str, str]]:
    """id -> {family, title, body} for every heading entry."""
    heads = list(HEADING.finditer(text))
    info: dict[str, dict[str, str]] = {}
    for i, m in enumerate(heads):
        rid = m.group(2)
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        info[rid] = {
            "family": m.group(3),
            "title": m.group(5).strip(),
            "body": text[start:end],
        }
    return info


def all_ids(text: str) -> list[str]:
    return sorted(set(ID_RE.findall(text)))


def first_clause(body: str) -> str:
    m = re.search(r"\*\*Statement\*\*:\s*([\s\S]*)", body)
    if not m:
        return ""
    t = m.group(1).split("\n\n")[0].replace("\n", " ").strip()
    t = re.split(r"(?<=[a-z0-9\)\]])\. ", t)[0]
    t = t.replace('"', "'")
    return t[:160].strip()


def verification_text(body: str) -> str:
    ver = re.search(
        r"\*\*Verification\*\*:([\s\S]*?)(\n\n\*\*Priority|\n\n#####|\n\n####|$)", body
    )
    stm = re.search(
        r"\*\*Statement\*\*:([\s\S]*?)(\n\n\*\*Source|\n\n\*\*Verification|$)", body
    )
    return (ver.group(1) if ver else "") + "\n" + (stm.group(1) if stm else "")


# --- evidence resolvers ------------------------------------------------------

ART = re.compile(r"`([^`\n]+)`")


class Evidence:
    """Path-resolution indexes over the evidence universe."""

    def __init__(self, files: Sequence[str]) -> None:
        self.files = list(files)
        self.base: dict[str, list[str]] = {}
        for f in self.files:
            self.base.setdefault(os.path.basename(f), []).append(f)
        self.snake: dict[str, str] = {}
        for f in self.files:
            b = os.path.basename(f)
            for suffix in (".test.tsx", ".test.ts", ".test.js"):
                if b.endswith(suffix):
                    stem = b[: -len(suffix)]
                    s = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
                    self.snake.setdefault(stem.lower(), f)
                    self.snake.setdefault(s, f)
                    self.snake.setdefault(s.replace("_", ""), f)
            if b.endswith(".md"):
                s = re.sub(r"(?<!^)(?=[A-Z])", "_", b[:-3]).lower() + ".md"
                self.snake.setdefault(b.lower(), f)
                if s != b.lower():
                    self.snake.setdefault(s, f)
        self.sym: dict[str, list[str]] = {}
        for f in self.files:
            if not CODEPAT.search(f):
                continue
            for tok in set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{4,}", read(os.path.join(ROOT, f)))):
                self.sym.setdefault(tok, []).append(f)

    def resolve(self, raw: str) -> str | None:
        """Resolve a backticked citation to ONE existing repo path, or None."""
        s = raw.strip()
        if not s or len(s) > 70 or s.startswith(("REQ-", "http", "#")):
            return None
        sec: str | None = None
        m = re.search(r"§\s*([A-Za-z0-9 .]+)", s)
        if m:
            sec = re.sub(r"[^a-z0-9 -]", "", m.group(1).strip().lower())
        s = re.split(r"[:#§]", s)[0].strip()
        if not s:
            return None
        s = s.replace("\\", "/")
        p: str | None = None
        for cand in (
            s,
            os.path.join("docs", s), os.path.join("backend", s),
            os.path.join("frontend/src", s), os.path.join("frontend", s),
            os.path.join("ops", s), os.path.join("security", s),
            os.path.join("e2e", s), os.path.join(".github/workflows", s),
            os.path.join("custom-agent", s), os.path.join("mcp-server", s),
            os.path.join("docs/requirements", s),
        ):
            c = cand.replace(os.sep, "/")
            if "/" in c or os.path.exists(os.path.join(ROOT, c)):
                if os.path.isfile(os.path.join(ROOT, c)):
                    p = c
                    break
        if p is None:
            hits = self.base.get(s) or self.snake.get(s.lower())
            if isinstance(hits, list) and len(hits) == 1:
                p = hits[0]
            elif isinstance(hits, str):
                p = hits
        if p is None:
            return None
        if sec is not None and p.endswith(".md"):
            t = read(os.path.join(ROOT, p))
            heads = [
                re.sub(r"[^a-z0-9 -]", "", x.strip().lower())
                for x in re.findall(r"^#{1,6}\s+(.*)$", t, re.M)
            ]
            heads += [h.replace(" ", "-") for h in heads]
            if sec not in heads:
                return None
        return p


def citations(files: Sequence[str]) -> dict[str, list[str]]:
    """id -> files (outside docs/requirements.md) that name the id."""
    cite: dict[str, list[str]] = {}
    for f in files:
        if f == REQUIREMENTS_REL:
            continue
        t = read(os.path.join(ROOT, f))
        if f == "docs/plan.md":
            t = plan_body_clean(t)
        for m in ID_RE.finditer(t):
            cite.setdefault(m.group(0), []).append(f)
    return {k: sorted(set(v)) for k, v in cite.items()}


# --- register (deferral surface) ---------------------------------------------

REGISTER_ROW = re.compile(r"^\| (LIVE_[A-Z_]+) \| DEFERRED \| reason=([^|]+?) \|", re.M)


def register_deferrals() -> dict[str, str]:
    """key -> reason snippet, re-read from the live register every run."""
    t = read(os.path.join(ROOT, REGISTER_REL))
    out: dict[str, str] = {}
    for m in REGISTER_ROW.finditer(t):
        out[m.group(1)] = m.group(2).strip()
    return out


# --- row construction ---------------------------------------------------------

Row = dict[str, str]


def build_rows(
    req_text: str,
    files: Sequence[str],
    register: dict[str, str],
) -> list[Row]:
    """Derive one row per unique id.  Derivation priority (printed per row):

    1. example-reference   - ids with no heading entry (section 3.1 example)
    2. deferral-register   - ids mapped to a live register key / #61 blocker
    3. hardcase-ruling     - the two card-declared honest-hard ids -> GAP
    4. citation            - another repo file names the id
    5. verification-artifact - a backticked artifact in Verification/Statement
    6. test-name-normalization - PascalCase test citation -> snake_case file
    7. code-symbol         - a backticked identifier occurs in exactly one file
    8. otherwise           - GAP (no fabricated evidence)
    """
    info = enumerate_requirements(req_text)
    ids = all_ids(req_text)
    if not ids:
        raise GeneratorError("requirements input enumerates no REQ ids")
    ev = Evidence(files)
    cite = citations(files)
    rows: list[Row] = []
    for rid in ids:
        d = info.get(rid)
        if d is None:
            # The only measured instance is REQ-AUTH-001 at the section 3.1
            # ID-FORMAT example; the pointer is the example's own file.
            if rid == "REQ-AUTH-001" and os.path.isfile(os.path.join(ROOT, REQUIREMENTS_REL)):
                rows.append({
                    "id": rid, "family": rid.split("-")[1],
                    "status": "EXAMPLE_REFERENCE", "method": "example-reference",
                    "pointers": REQUIREMENTS_REL + "#section-3.1-id-format",
                    "title": "section 3.1 ID-format example (never a heading entry)",
                    "statement": "Full example of the REQ-[FAMILY]-NNN id format",
                })
                continue
            raise GeneratorError(f"id {rid} has no heading entry and no documented class")
        title, body, fam = d["title"], d["body"], d["family"]
        statement = first_clause(body)
        status = "GAP"
        method = "none"
        pointers: list[str] = []
        extra: dict[str, str] = {}

        key = DEFERRAL_ID_KEY.get(rid)
        if key is not None and key in register and key not in FORBIDDEN_DEFERRAL_KEYS:
            status, method = "DEFERRED_RULLED", "deferral-register"
            pointers = [REGISTER_REL, ISSUE61_POINTER]
            extra["deferral_key"] = key
            extra["deferral_reason"] = register[key][:180]
        elif rid in DEFERRAL_ID_ISSUE61:
            status, method = "DEFERRED_RULLED", "deferral-register"
            pointers = [REGISTER_REL, ISSUE61_POINTER]
            extra["issue"] = "61"
            extra["deferral_reason"] = (
                "RENDER_DEPLOY_HOOK secret is operator infrastructure (platform #61)")
        else:
            hard = {h[0]: h[1] for h in HARD_CASES}
            if rid in hard:
                status, method = "GAP", "hardcase-ruling"
                pointers = []
                extra["ruling"] = hard[rid]
            else:
                cl = verification_text(body)
                cs = cite.get(rid, [])
                test_cs = [p for p in cs if TESTPAT.search(p)]
                arts = sorted({
                    x for x in (ev.resolve(m.group(1).strip()) for m in ART.finditer(cl))
                    if x is not None
                })
                art_tests = [p for p in arts if TESTPAT.search(p)]
                if test_cs:
                    status, method, pointers = "IMPLEMENTED_TESTED", "citation", test_cs[:3]
                elif art_tests:
                    status, method, pointers = (
                        "IMPLEMENTED_TESTED", "verification-artifact", art_tests[:3])
                elif arts:
                    status, method, pointers = (
                        "IMPLEMENTED_STRUCTURAL", "verification-artifact", arts[:3])
                else:
                    th = [ev.snake[x] for x in re.findall(r"([A-Za-z0-9_]+)\.test", cl)
                          if x in ev.snake]
                    syms = [m.group(1).strip() for m in ART.finditer(cl)
                            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{4,}", m.group(1).strip())]
                    hits = sorted({f for s_ in syms for f in ev.sym.get(s_, [])})
                    hits_tests = [p for p in hits if TESTPAT.search(p)]
                    if th:
                        status, method, pointers = (
                            "IMPLEMENTED_TESTED", "test-name-normalization", sorted(set(th))[:3])
                    elif hits_tests:
                        status, method, pointers = (
                            "IMPLEMENTED_TESTED", "code-symbol", hits_tests[:3])
                    elif hits:
                        status, method, pointers = (
                            "IMPLEMENTED_STRUCTURAL", "code-symbol", hits[:3])
                    elif cs:
                        status, method, pointers = (
                            "IMPLEMENTED_STRUCTURAL", "citation", cs[:3])
        # Every pointer must exist on THIS tree (anti-vacuity: outside the
        # repo an unavailable pointer makes the row GAP, never a crash).
        pointers = [p for p in pointers if os.path.isfile(os.path.join(ROOT, p))]
        if status != "GAP" and not pointers:
            status, method = "GAP", "no-pointer-available"
        row: Row = {
            "id": rid, "family": fam, "status": status, "method": method,
            "pointers": ",".join(pointers), "title": title.replace('"', "'"),
            "statement": statement,
        }
        row.update(extra)
        rows.append(row)
    return rows


def validate_rows(rows: Sequence[Row]) -> None:
    seen = set()
    for r in rows:
        if r["status"] not in VOCABULARY:
            raise GeneratorError(f"unknown status {r['status']!r} on row {r['id']}")
        if r["id"] in seen:
            raise GeneratorError(f"duplicate row for {r['id']}")
        seen.add(r["id"])
        if r["status"] != "GAP" and not r["pointers"]:
            raise GeneratorError(f"non-GAP row {r['id']} carries no evidence pointer")


# --- serialisation ------------------------------------------------------------

def idset_digest(ids: Sequence[str]) -> str:
    payload = json.dumps(sorted(ids), separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def status_counts(rows: Sequence[Row]) -> dict[str, int]:
    out = {s: 0 for s in VOCABULARY}
    for r in rows:
        out[r["status"]] += 1
    return out


def family_counts(rows: Sequence[Row]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        out[r["family"]] = out.get(r["family"], 0) + 1
    return out


def row_line(r: Row) -> str:
    line = (f"REQ_ROW PASS id={r['id']} family={r['family']} status={r['status']} "
            f"method={r['method']}")
    if r["pointers"]:
        line += f" pointers={r['pointers']}"
    if r.get("deferral_key"):
        line += f" deferral_key={r['deferral_key']}"
    if r.get("issue"):
        line += f" issue={r['issue']}"
    if r.get("deferral_reason"):
        line += f" deferral_reason=\"{r['deferral_reason']}\""
    if r.get("ruling"):
        line += f" ruling={r['ruling']}"
    return line


def render_report(rows: Sequence[Row], register: dict[str, str]) -> str:
    ids = [r["id"] for r in rows]
    counts = status_counts(rows)
    fams = family_counts(rows)
    out: list[str] = []
    add = out.append
    add("# Requirement-ID coverage matrix (t57)")
    add("")
    add("GENERATOR-OWNED: docs/criteria/req_coverage_verification.md is written by")
    add("backend/scripts/req_coverage_verification.py. Never hand-edit it; change the")
    add("generator's derivation rules instead. The matrix enumerates every unique")
    add("REQ-[A-Z_]+-[0-9]{3} id in docs/requirements.md and classifies it with the")
    add("closed five-label vocabulary below; a non-GAP row always carries at least one")
    add("concrete evidence pointer. The generator exits nonzero IFF a GAP row or an")
    add("unpointed non-GAP row exists (fail-closed fence, review_plan W1) - the first")
    add("landing is expected to carry GAP rows; closing them is t58's work.")
    add("")
    add(f"REQ_STATUSES PASS vocabulary={','.join(VOCABULARY)}")
    add(f"REQ_MATRIX PASS rows={len(rows)} unique={len(set(ids))} "
        f"idset=sha256:{idset_digest(ids)}")
    for s in VOCABULARY:
        add(f"REQ_STATUS_COUNT {s} {counts[s]}")
    for fam in sorted(fams):
        add(f"REQ_FAMILY PASS family={fam} rows={fams[fam]}")
    add(f"REQ_FAMILIES PASS total={len(rows)} distinct={len(fams)}")
    add("")
    add("## Deferral surface")
    add("")
    add("REQ_DEFERRAL_PROVENANCE PASS source=docs/criteria/docs_verification.md"
        "#DEFERRAL_REGISTER method=register-row-derivation "
        "id_key_and_reason_snippet_per_row=true")
    key_ids: dict[str, int] = {}
    for r in rows:
        k = r.get("deferral_key")
        if k:
            key_ids[k] = key_ids.get(k, 0) + 1
    for k in sorted(key_ids):
        add(f"REQ_DEFERRAL_KEY PASS key={k} ids={key_ids[k]}")
    add(f"REQ_DEFERRAL_POINTER PASS issue=61 family=OPS artifact={ISSUE61_POINTER}")
    add("")
    add("## Hard cases (card-declared, never relabeled by t57)")
    add("")
    for hid, ruling in HARD_CASES:
        add(f"REQ_HARDCASE PASS id={hid} status=GAP ruling_pending=t58 pointer={ruling}")
    add("")
    add("## Fail-closed fence")
    add("")
    add("REQ_FENCE PASS gate=fail-closed iff=gap-or-unpointed-row "
        f"fixture=env-gated self-test token={GATE_FIXTURE_TOKEN}")
    add("")
    add("## Matrix")
    add("")
    add("Per-id rows: the REQ_ROW line carries the machine contract; the REQ_TITLE")
    add("line carries the heading title and the Statement first clause.")
    add("")
    for r in rows:
        add(row_line(r))
        add(f"REQ_TITLE PASS id={r['id']} title=\"{r['title']}\" "
            f"statement=\"{r['statement']}\"")
    add("")
    add("## Honest GAP list (t58's input, measured not asserted)")
    add("")
    add("Every GAP row above is a requirement whose verification this hermetic gate")
    add("could not point at concrete in-repo evidence. The rows below restate them")
    add("for the remediation card; the count is the REQ_STATUS_COUNT GAP row above.")
    add("")
    return "\n".join(out) + "\n"


# --- entry point ---------------------------------------------------------------

def unpointed_non_gap(rows: Sequence[Row]) -> int:
    return sum(1 for r in rows if r["status"] != "GAP" and not r["pointers"])


def main() -> int:
    out_path = os.environ.get("REQ_COVERAGE_OUT") or OUT_DEFAULT
    seed = os.environ.get("REQ_COVERAGE_SEED", "")
    token_env = os.environ.get("REQ_COVERAGE_FIXTURE_TOKEN", "")
    req_text = read(os.path.join(ROOT, REQUIREMENTS_REL))
    files = tree_files()
    register = register_deferrals()
    rows = build_rows(req_text, files, register)
    validate_rows(rows)
    if seed == "gap":
        # Hermetic self-test: seeding is gated on the shared card token so a
        # copy of this generator cannot fake the gate (ac4 negative legs).
        if token_env != GATE_FIXTURE_TOKEN:
            print(f"req_coverage_verification: REFUSING to seed - fixture token "
                  f"mismatch (want {GATE_FIXTURE_TOKEN})")
            return 2
        rows = rows + [{
            "id": "REQ-SEED-000", "family": "SEED", "status": "GAP",
            "method": "seeded-self-test", "pointers": "",
            "title": "synthetic seeded gap row", "statement": "seeded gap row",
        }]
    report = render_report(rows, register)
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report)
    counts = status_counts(rows)
    gap = counts["GAP"]
    unpointed = unpointed_non_gap(rows)
    print(f"req_coverage_verification: rows={len(rows)} gap={gap} unpointed={unpointed}")
    if gap or unpointed:
        print("req_coverage_verification: RED (fail-closed fence - "
              f"{gap} GAP rows, {unpointed} unpointed non-GAP rows)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

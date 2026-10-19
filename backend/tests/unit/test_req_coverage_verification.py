"""Tests for the t57 per-REQ-ID coverage matrix generator.

The generator lives at backend/scripts/req_coverage_verification.py —
outside the importable package — so it is reached through an importlib
file loader (the t26 agent-hooks loader precedent).  The suite pins the
contract the card fences parse:

* the enumeration closes at the 749 unique ids of docs/requirements.md,
* the status vocabulary is CLOSED to the five declared labels and every
  member carries a REQ_STATUS_COUNT row (including zero counts),
* every non-GAP row carries at least one concrete evidence pointer,
* determinism: two runs on the same tree are byte-identical,
* the fail-closed exit-code fence is an IFF property, executed through
  the same code path the ac4 fence drives: a seeded GAP row makes
  ``main()`` return nonzero, a clean fixture makes it return zero, and
  seeding refuses to run under a wrong fixture token.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2].parent
SCRIPT = REPO_ROOT / "backend" / "scripts" / "req_coverage_verification.py"
REPORT = REPO_ROOT / "docs" / "criteria" / "req_coverage_verification.md"
REQUIREMENTS = REPO_ROOT / "docs" / "requirements.md"


def _load_generator() -> Any:
    """Load the path-held generator module (Any: dynamic loader)."""
    spec = importlib.util.spec_from_file_location("req_cov_gen", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen: Any = _load_generator()

TOKEN = hashlib.sha256(b"t57-gate-fixture-v1").hexdigest()[:16]


def _rows(text: str) -> list[str]:
    return [x for x in text.split("\n") if x.startswith("REQ_ROW PASS id=REQ-")]


def _machine(text: str, prefix: str) -> list[str]:
    return [x for x in text.split("\n") if x.startswith(prefix)]


def _run_in_root(tmp_path: Path, out: Path, seed: bool, token: str) -> int:
    """Run the generator with ROOT pointed at tmp_path via REQ_COVERAGE_OUT.

    The generator derives ROOT from its own file location, so the caller
    must have copied SCRIPT under tmp_path/backend/ first.
    """
    env = dict(os.environ)
    env["REQ_COVERAGE_OUT"] = str(out)
    env["REQ_COVERAGE_FIXTURE_TOKEN"] = token
    if seed:
        env["REQ_COVERAGE_SEED"] = "gap"
    else:
        env.pop("REQ_COVERAGE_SEED", None)
    proc = subprocess.run(
        [sys.executable, str(tmp_path / "backend" / "req_coverage_selftest.py")],
        env=env, capture_output=True, text=True, timeout=180, check=False,
    )
    return proc.returncode


def _mini_root(tmp_path: Path) -> Path:
    """A minimal ROOT: requirements + register copy + script copy."""
    (tmp_path / "docs" / "criteria").mkdir(parents=True)
    (tmp_path / "backend").mkdir(parents=True)
    (tmp_path / "docs" / "requirements.md").write_text(
        REQUIREMENTS.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "docs" / "criteria" / "docs_verification.md").write_text(
        (REPO_ROOT / "docs" / "criteria" / "docs_verification.md").read_text(
            encoding="utf-8"), encoding="utf-8")
    (tmp_path / "backend" / "req_coverage_selftest.py").write_text(
        SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def test_module_contract_rows_exist() -> None:
    assert SCRIPT.is_file()
    assert REPORT.is_file()
    assert gen.GATE_FIXTURE_TOKEN == TOKEN


def test_enumeration_closes_at_749_unique_ids() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    rows = _rows(text)
    assert len(rows) == 749
    ids = [x.split(" ")[2].split("=")[1] for x in rows]
    assert len(set(ids)) == 749
    source_ids = set(gen.ID_RE.findall(
        REQUIREMENTS.read_text(encoding="utf-8").replace("\r\n", "\n")))
    assert set(ids) == source_ids
    assert len(source_ids) == 749


def test_family_tally_closes_over_18_families() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    fam_rows = _machine(text, "REQ_FAMILY PASS family=")
    assert len(fam_rows) == 18
    total = sum(int(x.rsplit("=", 1)[1]) for x in fam_rows)
    assert total == 749
    assert "REQ_FAMILIES PASS total=749 distinct=18" in text


def test_idset_digest_matches_js_style_recomputation() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    header = _machine(text, "REQ_MATRIX PASS")[0]
    claimed = header.split("idset=sha256:")[1][:16]
    ids = set(gen.ID_RE.findall(
        REQUIREMENTS.read_text(encoding="utf-8").replace("\r\n", "\n")))
    payload = json.dumps(sorted(ids), separators=(",", ":"), ensure_ascii=False)
    assert claimed == hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def test_closed_vocabulary_declared_and_counted() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert ("REQ_STATUSES PASS vocabulary=IMPLEMENTED_TESTED,"
            "IMPLEMENTED_STRUCTURAL,DEFERRED_RULLED,GAP,EXAMPLE_REFERENCE" in text)
    for status in gen.VOCABULARY:
        assert _machine(text, f"REQ_STATUS_COUNT {status} "), f"no count row for {status}"
    seen = {x.split(" status=")[1].split(" ")[0] for x in _rows(text)}
    assert seen <= set(gen.VOCABULARY)


def test_every_non_gap_row_carries_a_pointer() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    for row in _rows(text):
        if " status=GAP " not in row:
            assert "pointers=" in row, row


def test_auth_001_is_the_example_reference_row() -> None:
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    rows = [x for x in _rows(text) if " id=REQ-AUTH-001 " in x]
    assert len(rows) == 1
    assert " status=EXAMPLE_REFERENCE " in rows[0]
    assert "docs/requirements.md" in rows[0]


def test_generator_is_hermetic_by_grep() -> None:
    src = SCRIPT.read_text(encoding="utf-8")
    for bad in ("import requests", "import httpx", "import socket",
                "import urllib", "import docker", "subprocess"):
        assert bad not in src, bad


def test_two_runs_are_byte_identical(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    out_a = root / "a.md"
    out_b = root / "b.md"
    rc_a = _run_in_root(root, out_a, seed=False, token=TOKEN)
    rc_b = _run_in_root(root, out_b, seed=False, token=TOKEN)
    assert rc_a == rc_b
    assert out_a.read_bytes() == out_b.read_bytes()


def test_unknown_status_is_a_generator_error() -> None:
    rows = [{"id": "REQ-X-1", "family": "X", "status": "GREENISH",
             "method": "test", "pointers": "README.md", "title": "t",
             "statement": "s"}]
    with pytest.raises(gen.GeneratorError):
        gen.validate_rows(rows)


def test_pointer_less_non_gap_row_is_a_generator_error() -> None:
    rows = [{"id": "REQ-X-1", "family": "X", "status": "IMPLEMENTED_TESTED",
             "method": "test", "pointers": "", "title": "t", "statement": "s"}]
    with pytest.raises(gen.GeneratorError):
        gen.validate_rows(rows)


def test_empty_input_never_yields_a_silently_short_matrix(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    (root / "docs" / "requirements.md").write_text("# nothing here\n", encoding="utf-8")
    assert _run_in_root(root, root / "out.md", seed=False, token=TOKEN) != 0
    assert not (root / "out.md").exists()


def test_seeded_gap_row_makes_main_return_nonzero(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    clean = root / "clean.md"
    _run_in_root(root, clean, seed=False, token=TOKEN)
    assert clean.is_file(), "the unseeded copy must write a full report"
    seeded = root / "seeded.md"
    rc = _run_in_root(root, seeded, seed=True, token=TOKEN)
    assert rc != 0, "the fail-closed fence must exit nonzero on a seeded GAP row"
    clean_rows = _rows(clean.read_text(encoding="utf-8"))
    seeded_rows = _rows(seeded.read_text(encoding="utf-8"))
    assert len(seeded_rows) == len(clean_rows) + 1


def test_clean_zero_gap_fixture_makes_main_return_zero(tmp_path: Path) -> None:
    """The IFF half the seeded test alone cannot prove: with zero GAP rows
    and zero unpointed rows main() must return 0."""
    real_root = gen.ROOT
    real_build = gen.build_rows
    real_register = gen.register_deferrals
    try:
        gen.ROOT = str(tmp_path)

        def fake_build(req_text: str, files: list[str],
                       register: dict[str, str]) -> list[dict[str, str]]:
            assert req_text == ""  # empty input must NOT raise here
            return [{"id": "REQ-FAKE-001", "family": "FAKE",
                     "status": "IMPLEMENTED_STRUCTURAL",
                     "method": "test-fixture", "pointers": "fixture-pointer.md",
                     "title": "t", "statement": "s"}]

        gen.build_rows = fake_build
        gen.register_deferrals = lambda: {}
        (tmp_path / "fixture-pointer.md").write_text("x", encoding="utf-8")
        out = tmp_path / "report.md"
        os.environ["REQ_COVERAGE_OUT"] = str(out)
        assert gen.main() == 0, "zero GAP + zero unpointed must exit 0 (iff)"
        text = out.read_text(encoding="utf-8")
        assert "REQ_STATUS_COUNT GAP 0" in text
    finally:
        os.environ.pop("REQ_COVERAGE_OUT", None)
        gen.ROOT = real_root
        gen.build_rows = real_build
        gen.register_deferrals = real_register


def test_wrong_fixture_token_refuses_to_seed(tmp_path: Path) -> None:
    root = _mini_root(tmp_path)
    out = root / "wrong.md"
    rc = _run_in_root(root, out, seed=True, token="0000000000000000")
    assert rc != 0
    assert not out.exists(), "a wrong-token seed must refuse WITHOUT writing"


# --- t58: the two card-declared rulings (platform #65) ----------------------

RULING_IDS = {
    "REQ-TECH-008": gen.RULING_TECH_DATEFNS_OVERRULED,
    "REQ-FE-121": gen.RULING_FE_PERF_LIVE_PROFILING,
}


def test_ruling_constants_are_static_and_not_register_shaped() -> None:
    """The two ruling keys are code constants, never register rows.

    The carried register parse is ^LIVE_, so a key starting with LIVE_
    would masquerade as a register row; and neither key may join the
    FORBIDDEN/DEFERRAL_ID_KEY surfaces the register derivation uses.
    """
    assert set(gen.STATIC_RULINGS) == set(RULING_IDS)
    for rid, key in RULING_IDS.items():
        assert gen.STATIC_RULINGS[rid][0] == key
        assert not key.startswith("LIVE_"), key
        assert key not in gen.FORBIDDEN_DEFERRAL_KEYS
        assert rid not in gen.DEFERRAL_ID_KEY and rid not in gen.DEFERRAL_ID_ISSUE61
        assert gen.STATIC_RULINGS[rid][1], "the reason snippet must be honest and non-empty"
    assert gen.RULINGS_ARTIFACT_REL == "docs/rulings/req-matrix.md"
    assert gen.RULING_ISSUE == "65"
    assert not hasattr(gen, "HARD_CASES"), "the forced-GAP HARD_CASES branch is gone"


def test_ruled_ids_close_as_deferred_ruled_with_key_pointer_and_reason() -> None:
    """Both ruled ids: DEFERRED_RULLED via the static branch, BEFORE citations.

    The mini ROOT (requirements + register + script copy only) carries no
    docs/rulings artifact, so the pointer-existence filter drops the
    rulings pointer and the row falls to GAP/no-pointer-available -
    proving the artifact is a real pointer, not a parsed input.  Against
    the repo tree the same rows carry key + issue 65 + pointer + reason.
    """
    files = gen.tree_files()
    register = gen.register_deferrals()
    rows = {r["id"]: r for r in gen.build_rows(
        REQUIREMENTS.read_text(encoding="utf-8").replace("\r\n", "\n"), files, register)}
    for rid, key in RULING_IDS.items():
        r = rows[rid]
        assert r["status"] == "DEFERRED_RULLED", r
        assert r["method"] == "card-declared-ruling", r
        assert r["deferral_key"] == key, r
        assert r["issue"] == "65", r
        assert r["deferral_reason"], r
        assert gen.RULINGS_ARTIFACT_REL in r["pointers"].split(","), r
        assert "docs/issues" not in r["pointers"], "no self-citation via a card"
    # The deferral branch runs before citations: even a tree whose only
    # naming file is a card cannot flip these rows to IMPLEMENTED_*.
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    for line in _rows(text):
        for rid, key in RULING_IDS.items():
            if f" id={rid} " in line:
                assert " status=DEFERRED_RULLED " in line, line
                assert f" deferral_key={key} " in line, line
                assert " issue=65 " in line, line
                assert "deferral_reason=" in line, line
                assert "docs/rulings/req-matrix.md" in line, line


def test_unruled_ids_are_unaffected_by_the_ruling_branch() -> None:
    """Unknown ids keep their old derivation: no ruling leaks a key."""
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    ruled = _machine(text, "REQ_HARDCASE PASS ")
    assert len(ruled) == 2
    for line in ruled:
        rid = line.split(" id=")[1].split(" ")[0]
        assert rid in RULING_IDS, line
        assert " status=DEFERRED_RULLED " in line, line
    key_rows = _machine(text, "REQ_DEFERRAL_KEY PASS key=")
    keys = {x.split("key=")[1].split(" ")[0] for x in key_rows}
    assert set(RULING_IDS.values()) <= keys
    carried = {k for k in keys if not k.startswith("RULING_")}
    assert carried == {"LIVE_AGENT_SESSION",
                       "LIVE_MCP_SUBPROCESS", "LIVE_SUBAGENT_LAUNCH"}
    # Only the two ruled rows carry a RULING_* key; no other row moved.
    for line in _rows(text):
        if " deferral_key=RULING_" in line:
            rid = line.split(" ")[2].split("=")[1]
            assert rid in RULING_IDS, line
    provenance = _machine(text, "REQ_DEFERRAL_PROVENANCE PASS ")
    assert any("source=docs/criteria/docs_verification.md#DEFERRAL_REGISTER" in p
               and "method=register-row-derivation" in p for p in provenance)
    assert any("source=docs/rulings/req-matrix.md" in p
               and "method=card-declared-ruling" in p for p in provenance)


T98_REATTESTED_IDS = ("REQ-OPS-061", "REQ-OPS-062", "REQ-CICD-041",
                      "REQ-DOC-070", "REQ-PROD-041")


def test_t98_live_deployment_state_is_no_longer_carried() -> None:
    """t98: the deployment went live, so LIVE_DEPLOYMENT_STATE left the register.

    The key must be absent from the committed report AND from the docs
    generator; the tally re-tallies to 10 DEFERRED_RULLED rows; the five ids
    the moved key used to back are re-attested exactly once each as
    IMPLEMENTED_TESTED with no deferral_key (a replacement, not a
    disappearance); and infra_verification.py names the -1qtu health host
    and never the old no-suffix host.
    """
    text = REPORT.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "LIVE_DEPLOYMENT_STATE" not in text, "the moved key lingers in the report"
    docs_src = (REPO_ROOT / "backend" / "scripts" / "docs_verification.py").read_text(
        encoding="utf-8").replace("\r\n", "\n")
    assert "LIVE_DEPLOYMENT_STATE" not in docs_src, "the docs register still carries the key"
    assert _machine(text, "REQ_STATUS_COUNT DEFERRED_RULLED 10 ") or \
        "REQ_STATUS_COUNT DEFERRED_RULLED 10" in text, "DEFERRED_RULLED did not re-tally to 10"
    rows = _rows(text)
    for rid in T98_REATTESTED_IDS:
        hit = [line for line in rows if f" id={rid} " in line]
        assert len(hit) == 1, rid + " is not present exactly once"
        assert " status=IMPLEMENTED_TESTED " in hit[0], rid + " is not IMPLEMENTED_TESTED"
        assert " deferral_key=" not in hit[0], rid + " still carries a deferral_key"
    assert not [line for line in rows if " deferral_key=LIVE_DEPLOYMENT_STATE " in line]
    infra_src = (REPO_ROOT / "backend" / "scripts" / "infra_verification.py").read_text(
        encoding="utf-8").replace("\r\n", "\n")
    assert "expense-tracker-dashboard-1qtu.onrender.com/api/v1/health" in infra_src
    assert "https://expense-tracker-dashboard.onrender.com" not in infra_src


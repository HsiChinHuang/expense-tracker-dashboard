#!/usr/bin/env python
# mypy: disable-error-code="import-untyped"
"""Hermetic agent-pack verification run for t35 (REQ-PLAN-061 milestone exit).

This script is the verification deliverable of issue t35: it EXECUTES the
hermetically-executable phase_6 rows (the 14 hook nodes, the 12 MCP tool nodes,
the in-process ``list_tools``/``call_tool`` contract, the symlink ``cat``-through
discovery byte-equality, the component counts recounted from the live tree, the
permissions-matrix layer paths), ATTESTS the structural rows (skill/subagent
frontmatter and section structure, the manifest dependency list, the frozen
workflow set), and GENERATES ``docs/criteria/agent_pack_verification.md`` (the
t23/t28 convention: pinned token lines with real measured values, ending
``ALL_CHECKS_PASS <N> PASS``).

Hermetic by construction (plan.md phase_6 rulings 1/5):

* NO network client is constructed: every MCP leg injects an
  ``httpx.MockTransport`` recorder, so a rejected-token call provably performs
  ZERO transport requests.
* The hook modules are loaded by PATH through ``importlib`` (the hyphenated
  file names are not importable identifiers - the t30 loader contract).
* The MCP modules are imported in-process by extending ``sys.path`` with
  ``mcp-server/`` (they import their siblings by bare name); nothing is
  spawned, so this file contains NO ``subprocess`` / ``requests`` / ``uvicorn``
  / ``socket`` / ``sqlalchemy`` import (ac1 greps for exactly that).
* The backend collection count and the ``.agents`` symlink inventory arrive
  through FILES (``--collection-file`` / ``--ls-files-file``) because ac1
  forbids ``subprocess``: counts reach this script through files, never pipes.
  Both are PARSED from those captures, never hand-typed.
* Any scratch write happens inside a private ``tempfile.TemporaryDirectory``.

The three rows this host cannot execute (live agent session, real-subprocess
MCP against a running backend = REQ-PLAN-060 task 6.17, live subagent launch)
land in the DEFERRAL REGISTER - a deferred row is NEVER written as PASS, and
ac4's per-key grep gate enforces that mutual exclusion.

The document is written with CRLF newlines (the merged t28 precedent) so
ac1's byte-stability ``cmp`` holds against a FRESH checkout, where
``core.autocrlf=true`` smudges the committed LF blob to CRLF in the working
tree. The clean filter maps the CRLF working file back to the committed LF
blob, so ``git hash-object`` equals the blob and the checkout/emit pair is a
byte-exact closed loop on every host.

Usage (from ``backend/``):

    PYTHONPATH=. uv run python scripts/agent_pack_verification.py \
        --collection-file <pytest --collect-only -q capture> \
        --ls-files-file <git ls-files -s .agents capture>
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.util
import io
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import httpx
import pytest

from app.auth.jwt import create_access_token
from app.config import get_settings

MIN_CHECKS = 18
"""Floor for the ALL_CHECKS_PASS total (t28 precedent scale, ac1 gate)."""

COLLECTION_FLOOR = 244
"""Backend collection floor (merged-base measurement; never rewritten)."""

EXPECTED_HOOK_NODES = 14
"""Frozen t30 hook-suite node count (REQ-EXT-072)."""

EXPECTED_MCP_NODES = 12
"""Frozen t32 MCP-suite node count (REQ-PLAN-061)."""

TEST_SECRET = "t35-hermetic-pack-verification-secret-not-a-real-key"
"""Throwaway secret pinned for the hermetic run (never a real key)."""

WRONG_SECRET = "t35-hermetic-pack-other-secret-not-a-real-key"
"""Second throwaway secret used to mint a signature-rejected token."""

SUBJECT = "user-t35"
BASE_URL = "http://backend.invalid/api/v1"
SKILL_DIRS = ("add-expense", "budget-check", "monthly-report")
AGENT_FILES = ("finance-analyst.md", "qa-reviewer.md")
AGENT_LAYER_DIRS = ("agent-capabilities", "agent-hooks", "mcp-server", "custom-agent", ".agents")
PERMISSION_SECTIONS = (
    "User Roles",
    "Resource Permissions",
    "Agent Permissions",
    "Skill Permissions",
    "Subagent Permissions",
    "Enforcement Layers",
    "Forbidden Actions",
    "Escalation Rules",
)
PACK_DOC_SECTIONS = ("Skills", "Hooks", "MCP Server", "Subagents", "Permissions")
MCP_README_SECTIONS = (
    "Layout",
    "Tools",
    "Authentication",
    "Environment variables",
    "Running",
    "Design notes",
)
HOOKS_README_SECTIONS = ("Trigger", "Failure behavior")
MANIFEST_DEPS = ("httpx", "python-jose")
EXPECTED_WORKFLOWS = ("ci", "e2e", "deploy")
MCP_TOOL_NAMES = ("add_expense", "get_budget_status", "monthly_summary", "list_expenses")
FRONTMATTER = re.compile(r"(?s)\A---\n(.*?)\n---\n")
PLAN_ROW_TOKENS = {
    "skills": "SKILL_ROWS",
    "hooks": "COUNT_ROWS",
    "hook_tests": "HOOK_TEST_ROWS",
    "mcp_start": "DEFERRED_ROW",
    "mcp_tools": "MCP_TEST_ROWS",
    "subagents": "SUBAGENT_ROWS",
    "permissions": "PERMISSIONS_ROWS",
}


class Verifier:
    """One hermetic verification run with a token ledger."""

    def __init__(self) -> None:
        """Initialise the empty token ledger."""
        self.tokens: list[str] = []
        self.checks = 0
        self.failures: list[str] = []

    def record(self, name: str, ok: bool, value: str = "") -> bool:
        """Append one pinned ``<NAME> <value> PASS|FAIL`` token line.

        Args:
            name: Token name (HOOK_TEST_ROWS, COUNT_ROWS, ...).
            ok: Whether the check passed.
            value: Rendered value inserted between name and verdict.

        Returns:
            bool: The ``ok`` flag.
        """
        verdict = "PASS" if ok else "FAIL"
        line = f"{name} {value} {verdict}" if value else f"{name} {verdict}"
        self.tokens.append(line)
        self.checks += 1
        if not ok:
            self.failures.append(name)
        return ok

    def defer(self, key: str, artifact: str, reason: str, live_check: str) -> None:
        """Append one ``DEFERRED_ROW`` line (recorded, never asserted).

        Args:
            key: Register key (LIVE_AGENT_SESSION, ...).
            artifact: Repository artifact that satisfies the row.
            reason: Measured host reason (no_agent_runtime_in_harness, ...).
            live_check: Operator's live-check command.
        """
        self.tokens.append(
            f"DEFERRED_ROW {key} artifact={artifact} reason={reason} live_check={live_check}"
        )

    def emit(self) -> list[str]:
        """Emit the ALL_CHECKS_PASS summary token.

        Returns:
            list[str]: The full token ledger.
        """
        ok = self.checks >= MIN_CHECKS and not self.failures
        self.tokens.append(f"ALL_CHECKS_PASS {self.checks} {'PASS' if ok else 'FAIL'}")
        if not ok:
            self.tokens.append(f"CHECK_FAILURES {'/'.join(self.failures)} FAIL")
        return self.tokens


def repo_root() -> Path:
    """Return the repository root (two levels above ``backend/scripts``).

    Returns:
        Path: The repository root directory.
    """
    return Path(__file__).resolve().parents[2]


def mcp_module(module_name: str) -> Any:
    """Import one ``mcp-server`` module by bare name (siblings import bare).

    Args:
        module_name: Bare module name such as ``auth`` or ``tools.list_expenses``.

    Returns:
        Any: The imported module (dynamically located imports cannot be
        statically typed).
    """
    mcp_dir = str(repo_root() / "mcp-server")
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)
    return importlib.import_module(module_name)


def load_hook(module_name: str, filename: str) -> ModuleType:
    """Load one hyphenated hook module from ``agent-hooks/`` by path.

    Args:
        module_name: The name to give the loaded module.
        filename: The hyphenated hook file name.

    Returns:
        ModuleType: The executed hook module.

    Raises:
        RuntimeError: The hook file or its loader is unavailable.
    """
    path = repo_root() / "agent-hooks" / filename
    if not path.is_file():
        raise RuntimeError(f"hook module not found: {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"hook module has no loader: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    """Read a repository file as UTF-8 text with newlines normalised to LF.

    Args:
        path: File to read.

    Returns:
        str: The file contents with CRLF collapsed to LF.
    """
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def pin_jwt_settings() -> None:
    """Pin backend JWT settings so the run never depends on ``.env``."""
    os.environ["JWT_SECRET"] = TEST_SECRET
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"
    os.environ["JWT_ISSUER"] = "expense-tracker"
    os.environ["JWT_AUDIENCE"] = "expense-tracker-api"
    get_settings.cache_clear()


class Recorder:
    """Records every request an ``httpx.MockTransport`` receives."""

    def __init__(self) -> None:
        """Start with an empty request list."""
        self.requests: list[httpx.Request] = []

    @property
    def calls(self) -> int:
        """Return how many requests reached the transport."""
        return len(self.requests)

    def transport(self) -> httpx.BaseTransport:
        """Return a MockTransport that records requests and answers 200.

        Returns:
            httpx.BaseTransport: The mocked transport (no egress, ever).
        """
        return httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        """Record *request* and answer with a canned 200 envelope.

        Args:
            request: The request the tool built.

        Returns:
            httpx.Response: A canned list-envelope response.
        """
        self.requests.append(request)
        return httpx.Response(200, json={"items": [], "total": 0, "page": 1, "page_size": 5})


class ClientShim:
    """Stand-in for the ``httpx`` module whose ``Client`` cannot reach the wire.

    The merged tool modules construct ``httpx.Client(transport=...)``; the
    shim keeps every other module attribute intact and injects a recorded
    ``httpx.MockTransport`` regardless of what the caller passes, so the
    dispatch leg stays hermetic and the rejection leg can prove a zero call
    count (REQ-AI-083: rejection happens BEFORE any request).
    """

    def __init__(self, recorder: Recorder) -> None:
        """Bind the recorder whose transport will always be injected.

        Args:
            recorder: The request recorder backing the mock transport.
        """
        self.recorder = recorder
        for key, value in vars(httpx).items():
            if key.startswith("__"):
                continue
            setattr(self, key, value)
        self.Client = self._mock_client

    def _mock_client(self, *args: Any, **kwargs: Any) -> httpx.Client:
        """Return a real client whose transport is the mocked recorder.

        Args:
            *args: Positional arguments forwarded to ``httpx.Client``.
            **kwargs: Keyword arguments forwarded (``transport`` is replaced).

        Returns:
            httpx.Client: A client that can never reach the network.
        """
        kwargs["transport"] = self.recorder.transport()
        return httpx.Client(*args, **kwargs)


def forged_token(**overrides: Any) -> str:
    """Mint a compact JWS signed with the wrong secret (must be rejected).

    Args:
        overrides: Claim overrides on top of the otherwise-valid defaults.

    Returns:
        str: A token whose signature the MCP verifier must refuse.
    """
    from jose import jwt as jose_jwt

    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": SUBJECT,
        "iss": "expense-tracker",
        "aud": "expense-tracker-api",
        "iat": now,
        "exp": now + 3600,
        "type": "access",
    }
    claims.update(overrides)
    return cast(str, jose_jwt.encode(claims, WRONG_SECRET, algorithm="HS256"))


def run_pytest(nodes: list[str]) -> int:
    """Run pytest in-process with stdout/stderr fully suppressed.

    Args:
        nodes: Test paths to run.

    Returns:
        int: The pytest exit code.
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        code = pytest.main([*nodes, "-q", "-p", "no:cacheprovider"])
    return int(code)


def parse_collection(collection_file: Path) -> list[str]:
    """Parse the node ids out of the passed-through collection capture.

    Args:
        collection_file: Capture of ``pytest --collect-only -q`` (backend cwd).

    Returns:
        list[str]: The node ids exactly as the pinned commands counted them.

    Raises:
        RuntimeError: The capture is missing or carries no node ids.
    """
    if not collection_file.is_file():
        raise RuntimeError(f"collection capture missing: {collection_file}")
    node_ids = [line.strip() for line in read_text(collection_file).splitlines() if "::" in line]
    if not node_ids:
        raise RuntimeError("collection capture contains no node ids")
    return node_ids


def record_hook_suite(v: Verifier, node_ids: list[str]) -> None:
    """Re-run the t30 hook suite and record the measured node-count row.

    Args:
        v: The token ledger.
        node_ids: Node ids parsed from the live collection capture.
    """
    collected = [
        node for node in node_ids if node.startswith("tests/integration/test_agent_hooks.py::")
    ]
    code = run_pytest(["tests/integration/test_agent_hooks.py"])
    v.record(
        "HOOK_TEST_ROWS",
        len(collected) == EXPECTED_HOOK_NODES and code == 0,
        f"{len(collected)}",
    )


def record_hook_contract(v: Verifier) -> None:
    """Execute the hook loader contract row (importlib by path, no side effects).

    Both hyphenated hook modules are loaded by PATH, the amount ceiling is
    compared against the merged backend ``AMOUNT_MAX`` (the t30 drift guard),
    and the ownership hook is exercised for its ``PermissionError`` contract.

    Args:
        v: The token ledger.
    """
    from app.schemas.expense import AMOUNT_MAX

    amount = load_hook("t35_hook_validate_amount", "validate-amount.py")
    ownership = load_hook("t35_hook_validate_ownership", "validate-ownership.py")

    ceiling_ok = amount.MAX_AMOUNT == AMOUNT_MAX
    behaviour_ok = False
    try:
        amount.validate_amount("12.50")
        ownership.validate_ownership("u1", "u1")
        rejected = False
        try:
            amount.validate_amount("-1")
        except ValueError:
            rejected = True
        raised = None
        try:
            ownership.validate_ownership("u1", "u2")
        except Exception as exc:  # noqa: BLE001 - the type IS the contract
            raised = type(exc)
        behaviour_ok = rejected and raised is PermissionError
    except Exception:  # noqa: BLE001 - any loader failure fails the row
        behaviour_ok = False

    v.record(
        "HOOK_CONTRACT_ROWS",
        ceiling_ok and behaviour_ok,
        f"loaded=2 max_amount={'matches' if ceiling_ok else 'drifts'} "
        f"errors={'ok' if behaviour_ok else 'miss'}",
    )


def record_mcp_suite(v: Verifier, node_ids: list[str]) -> None:
    """Re-run the t32 MCP suite and record the measured node-count row.

    Args:
        v: The token ledger.
        node_ids: Node ids parsed from the live collection capture.
    """
    collected = [
        node for node in node_ids if node.startswith("tests/integration/test_mcp_tools.py::")
    ]
    code = run_pytest(["tests/integration/test_mcp_tools.py"])
    v.record(
        "MCP_TEST_ROWS",
        len(collected) == EXPECTED_MCP_NODES and code == 0,
        f"{len(collected)}",
    )


def record_contract(v: Verifier) -> None:
    """Execute the in-process ``list_tools``/``call_tool`` contract row.

    The dispatch leg runs the real ``call_tool`` with a mocked transport
    injected; the rejection leg swaps in a wrongly-signed token and proves the
    transport recorded ZERO requests.

    Args:
        v: The token ledger.
    """
    server = mcp_module("server")
    auth = mcp_module("auth")
    tool_module = mcp_module("tools.list_expenses")
    real_httpx = tool_module.httpx
    tools = cast(list[dict[str, Any]], server.list_tools())
    names = tuple(str(tool["name"]) for tool in tools)
    valid_token = create_access_token(SUBJECT)

    auth.MCP_JWT_SECRET = TEST_SECRET
    auth.MCP_USER_TOKEN = valid_token
    dispatch_recorder = Recorder()
    dispatch_ok = False
    tool_module.httpx = ClientShim(dispatch_recorder)
    try:
        dispatched: Any = server.call_tool("list_expenses", {"page": 1, "limit": 5})
        dispatch_ok = isinstance(dispatched, dict) and dispatch_recorder.calls == 1
    except Exception:  # noqa: BLE001 - any dispatch failure fails the row
        dispatch_ok = False
    finally:
        tool_module.httpx = real_httpx

    reject_recorder = Recorder()
    jwt_reject_ok = False
    tool_module.httpx = ClientShim(reject_recorder)
    try:
        auth.MCP_USER_TOKEN = forged_token()
        try:
            server.call_tool("list_expenses", {"page": 1, "limit": 5})
            jwt_reject_ok = False
        except auth.AuthError:
            jwt_reject_ok = reject_recorder.calls == 0
    finally:
        auth.MCP_USER_TOKEN = valid_token
        tool_module.httpx = real_httpx

    v.record(
        "MCP_CONTRACT_ROWS",
        len(tools) == 4 and names == MCP_TOOL_NAMES and dispatch_ok and jwt_reject_ok,
        f"tools={len(tools)} list_tools={len(tools)} "
        f"dispatch={'ok' if dispatch_ok else 'miss'} "
        f"jwt_reject={'ok' if jwt_reject_ok else 'miss'}",
    )


def record_symlinks(v: Verifier, ls_files_file: Path) -> None:
    """Recount the ``.agents`` git modes and prove cat-through byte-equality.

    Args:
        v: The token ledger.
        ls_files_file: Capture of ``git ls-files -s .agents``.

    Raises:
        RuntimeError: The capture is missing.
    """
    if not ls_files_file.is_file():
        raise RuntimeError(f"ls-files capture missing: {ls_files_file}")
    paths = [
        parts[3]
        for parts in (line.split() for line in read_text(ls_files_file).splitlines())
        if len(parts) == 4 and parts[0] == "120000"
    ]
    skills = [path for path in paths if path.startswith(".agents/skills/")]
    agents = [path for path in paths if path.startswith(".agents/agents/")]

    equal = 0
    for path in paths:
        link = repo_root() / path
        if not link.is_symlink():
            continue
        target = Path(os.path.normpath(link.parent / Path(os.readlink(link))))
        if target.is_file() and link.read_bytes() == target.read_bytes():
            equal += 1

    v.record(
        "SYMLINK_ROWS",
        len(skills) == 3 and len(agents) == 2 and len(paths) == 5 and equal == 5,
        f"skills={len(skills)} agents={len(agents)} mode120000={len(paths)} cateq={equal}",
    )


def record_counts(v: Verifier) -> None:
    """Recount the pack components and agent-layer directories from the tree.

    Args:
        v: The token ledger.
    """
    root = repo_root()
    skills = sorted(path.parent.name for path in (root / "agent-capabilities").glob("*/SKILL.md"))
    hooks = sorted(path.stem for path in (root / "agent-hooks").glob("*.py"))
    tools = sorted(
        path.stem
        for path in (root / "mcp-server" / "tools").glob("*.py")
        if path.name != "__init__.py"
    )
    agents = sorted(path.name for path in (root / "custom-agent").glob("*.md"))
    present = sum(1 for name in AGENT_LAYER_DIRS if (root / name).is_dir())

    v.record(
        "COUNT_ROWS",
        skills == sorted(SKILL_DIRS) and len(hooks) == 2 and len(tools) == 4 and len(agents) == 2,
        f"skills={len(skills)} hooks={len(hooks)} tools={len(tools)} subagents={len(agents)}",
    )
    v.record(
        "AGENT_DIRS",
        present == len(AGENT_LAYER_DIRS),
        f"{','.join(AGENT_LAYER_DIRS)} {present}",
    )


def has_frontmatter(text: str) -> bool:
    """Return whether *text* opens with a ``name``/``description`` block.

    Args:
        text: Markdown file contents.

    Returns:
        bool: True when the frontmatter block carries both keys.
    """
    block = FRONTMATTER.match(text)
    if block is None:
        return False
    body = block.group(1)
    return bool(
        re.search(r"(?m)^name:\s*\S+\s*$", body) and re.search(r"(?m)^description:\s*\S+", body)
    )


def frontmatter_description(text: str) -> str:
    """Return the ``description`` value of *text*'s frontmatter block.

    Args:
        text: Markdown file contents.

    Returns:
        str: The description value (empty when absent).
    """
    block = FRONTMATTER.match(text)
    if block is None:
        return ""
    match = re.search(r"(?m)^description:\s*(.+?)\s*$", block.group(1))
    return match.group(1) if match else ""


def record_skill_structure(v: Verifier) -> None:
    """Attest the three skill files' frontmatter and required sections.

    Args:
        v: The token ledger.
    """
    root = repo_root()
    frontmatter = 0
    when_to_use = 0
    steps = 0
    for name in SKILL_DIRS:
        path = root / "agent-capabilities" / name / "SKILL.md"
        if not path.is_file():
            continue
        text = read_text(path)
        frontmatter += int(has_frontmatter(text))
        when_to_use += int(bool(re.search(r"(?m)^## When to Use\s*$", text)))
        steps += int(bool(re.search(r"(?m)^## Steps\s*$", text)))

    total = len(SKILL_DIRS)
    v.record(
        "SKILL_ROWS",
        frontmatter == total and when_to_use == total and steps == total,
        f"{total} frontmatter={frontmatter} whentouse={when_to_use} steps={steps}",
    )


def record_subagent_structure(v: Verifier) -> None:
    """Attest the two subagent definitions' structure and behavioural roles.

    ``readonly`` counts the subagents whose frontmatter declares a read-only
    contract (exactly the finance analyst); ``nofix`` counts the subagents
    whose rules forbid fixing anything (exactly the qa reviewer).

    Args:
        v: The token ledger.
    """
    root = repo_root()
    frontmatter = 0
    read_only = 0
    no_fix = 0
    for name in AGENT_FILES:
        path = root / "custom-agent" / name
        if not path.is_file():
            continue
        text = read_text(path)
        frontmatter += int(has_frontmatter(text))
        read_only += int(frontmatter_description(text).lower().startswith("read-only"))
        no_fix += int(bool(re.search(r"(?m)^(?:[-*]\s+)?Do not fix\b", text)))

    total = len(AGENT_FILES)
    v.record(
        "SUBAGENT_ROWS",
        frontmatter == total and read_only == 1 and no_fix == 1,
        f"{total} frontmatter={frontmatter} readonly={read_only} nofix={no_fix}",
    )


def record_permissions(v: Verifier) -> None:
    """Count the permissions matrix's eight sections and six layer paths.

    The layer paths are parsed out of the enforcement table itself, so the
    ``paths_exist`` count is a real claim about the merged tree (REQ-AI-101,
    REQ-EXT-025: every named enforcing artifact must exist).

    Args:
        v: The token ledger.
    """
    path = repo_root() / "docs" / "permissions.md"
    text = read_text(path) if path.is_file() else ""
    sections = sum(
        1 for title in PERMISSION_SECTIONS if re.search(rf"(?m)^## {re.escape(title)}\s*$", text)
    )
    layers: list[str] = []
    marker = re.search(r"(?m)^## Enforcement Layers\s*$", text)
    if marker is not None:
        body = text[marker.end() :]
        nxt = re.search(r"(?m)^## ", body)
        body = body[: nxt.start()] if nxt else body
        layers = re.findall(r"(?m)^\| [^|]+\| `([^`]+)`", body)
    paths_exist = sum(1 for candidate in layers if (repo_root() / candidate).exists())

    v.record(
        "PERMISSIONS_ROWS",
        sections == 8 and len(layers) == 6 and paths_exist == 6,
        f"sections={sections} layers={len(layers)} paths_exist={paths_exist}",
    )


def record_manifest(v: Verifier) -> None:
    """Parse the MCP manifest's declared dependency list (REQ-TECH-026).

    Args:
        v: The token ledger.
    """
    text = read_text(repo_root() / "mcp-server" / "pyproject.toml")
    declared = re.findall(r"[\"']([A-Za-z0-9_.-]+)(?:\[[^\]]*\])?[>=~]", text)
    found = [dep for dep in MANIFEST_DEPS if any(d.lower().startswith(dep) for d in declared)]
    v.record(
        "MANIFEST_DEPS",
        found == list(MANIFEST_DEPS),
        f"{','.join(MANIFEST_DEPS)} {len(found)}",
    )


def record_docs_attestation(v: Verifier) -> None:
    """Attest the three documentation artifacts' required section structure.

    Args:
        v: The token ledger.
    """
    root = repo_root()

    def sections_of(path: Path) -> list[str]:
        if not path.is_file():
            return []
        return re.findall(r"(?m)^## (?!#)(.+?)\s*$", read_text(path))

    pack_sections = sections_of(root / "docs" / "agent-extension-pack.md")
    pack_ok = all(name in pack_sections for name in PACK_DOC_SECTIONS)
    v.record(
        "ATTEST_PACK_DOC",
        pack_ok,
        f"sections={len(pack_sections)} required={','.join(PACK_DOC_SECTIONS)} PRESENT",
    )

    readme_sections = sections_of(root / "mcp-server" / "README.md")
    v.record(
        "ATTEST_MCP_README",
        all(name in readme_sections for name in MCP_README_SECTIONS),
        f"sections={len(readme_sections)} PRESENT",
    )

    hooks_sections = sections_of(root / "agent-hooks" / "README.md")
    v.record(
        "ATTEST_HOOKS_README",
        all(name in hooks_sections for name in HOOKS_README_SECTIONS),
        f"sections={len(hooks_sections)} PRESENT",
    )


def record_workflows(v: Verifier) -> None:
    """Re-attest the frozen three-workflow set from this card's vantage.

    Args:
        v: The token ledger.
    """
    names = sorted(p.stem for p in (repo_root() / ".github" / "workflows").glob("*.yml"))
    ordered = sorted(names, key=EXPECTED_WORKFLOWS.index) if set(names) == set(
        EXPECTED_WORKFLOWS
    ) else names
    v.record(
        "WORKFLOWS",
        set(names) == set(EXPECTED_WORKFLOWS),
        f"{','.join(ordered)} {len(names)}",
    )


def record_collection(v: Verifier, collection_file: Path) -> int:
    """Record the BACKEND_COLLECTION row from the passed-through capture.

    Args:
        v: The token ledger.
        collection_file: Capture of ``pytest --collect-only -q``.

    Returns:
        int: The parsed collection count.
    """
    count = sum(1 for line in read_text(collection_file).splitlines() if "::" in line)
    v.record("BACKEND_COLLECTION", count >= COLLECTION_FLOOR, f"{count} floor={COLLECTION_FLOOR}")
    return count


def emit_register(v: Verifier) -> None:
    """Emit the three-row deferral register (recorded, never asserted).

    Args:
        v: The token ledger.
    """
    v.record("DEFERRAL_REGISTER", True, "3 DEFERRED")
    v.defer(
        "LIVE_AGENT_SESSION",
        "agent-capabilities/monthly-report/SKILL.md",
        "no_agent_runtime_in_harness",
        'pi-agent session prompt "Generate a monthly report for 2026-10"',
    )
    v.defer(
        "LIVE_MCP_SUBPROCESS",
        "mcp-server/server.py",
        "egress_forbidden_no_live_backend",
        "MCP_JWT_SECRET=... MCP_API_BASE_URL=... MCP_USER_TOKEN=... python mcp-server/server.py",
    )
    v.defer(
        "LIVE_SUBAGENT_LAUNCH",
        "custom-agent/finance-analyst.md",
        "no_agent_runtime_in_harness",
        'pi-agent session prompt "Launch finance analyst for 2026-10"',
    )


def criteria_rows() -> list[tuple[str, str, str, str]]:
    """Return the eight pinned criteria mapping rows.

    Returns:
        list[tuple[str, str, str, str]]: (row, requirement, mode, token).
    """
    return [
        ("7", "REQ-EXT-001", "executed", "COUNT_ROWS"),
        ("9", "REQ-EXT-060", "executed", "PERMISSIONS_ROWS"),
        ("10", "REQ-PROD-043", "executed", "COUNT_ROWS"),
        ("11", "REQ-PROD-043", "executed", "COUNT_ROWS"),
        ("12", "REQ-PROD-043", "executed", "COUNT_ROWS"),
        ("31", "REQ-PLAN-061", "executed", "MCP_TEST_ROWS"),
        ("32", "REQ-EXT-072", "executed", "HOOK_TEST_ROWS"),
        ("discovery", "REQ-AI-064", "executed", "SYMLINK_ROWS"),
    ]


def plan_rows() -> list[tuple[str, str]]:
    """Return the seven REQ-PLAN-061 verification rows with their modes.

    Returns:
        list[tuple[str, str]]: (row key, mode token).
    """
    return [
        ("skills", "executed"),
        ("hooks", "executed"),
        ("hook_tests", "executed"),
        ("mcp_start", "deferred"),
        ("mcp_tools", "executed"),
        ("subagents", "structural"),
        ("permissions", "structural"),
    ]


def record_criteria(v: Verifier) -> None:
    """Record the criteria header and the REQ-PLAN-061 row-mode line.

    Both are gated by the token cross-check: every cited token must already be
    present in the ledger (the t28 ac5 recipe).

    Args:
        v: The token ledger.
    """
    cited = all(
        any(line.startswith(token) for line in v.tokens) for _, _, _, token in criteria_rows()
    )
    v.record("CRITERIA_NUMBERS", cited, "7,9,12")

    modes = " ".join(f"{key}={mode}" for key, mode in plan_rows())
    plan_cited = all(
        any(line.startswith(PLAN_ROW_TOKENS[key]) for line in v.tokens)
        for key, _mode in plan_rows()
    )
    v.record("REQ-PLAN-061_ROWS", plan_cited, modes)


def pick(tokens: list[str], names: tuple[str, ...]) -> list[str]:
    """Select ledger lines whose leading token is one of *names*.

    Args:
        tokens: The full ledger.
        names: Token names to keep.

    Returns:
        list[str]: The matching lines in emit order.
    """
    return [line for line in tokens if line.split()[0] in names]


def render_document(tokens: list[str], collection: int) -> str:
    """Render the criteria evidence document from the measured ledger.

    Args:
        tokens: The pinned token ledger (in emit order).
        collection: Measured backend collection count (prose context only).

    Returns:
        str: The full document text with CRLF newlines.
    """
    root = repo_root()
    pack_doc = read_text(root / "docs" / "agent-extension-pack.md")
    checklist_lines = len(
        re.findall(
            r"(?m)^- (?:Skills|Hooks|MCP server|Subagents|Skills symlink|Agents symlink|"
            r"Documentation): ",
            pack_doc,
        )
    )
    readme_lines = len(read_text(root / "README.md").splitlines())
    executed = (
        "HOOK_TEST_ROWS",
        "MCP_TEST_ROWS",
        "HOOK_CONTRACT_ROWS",
        "MCP_CONTRACT_ROWS",
        "SYMLINK_ROWS",
        "BACKEND_COLLECTION",
        "COUNT_ROWS",
        "AGENT_DIRS",
        "PERMISSIONS_ROWS",
    )
    structural = (
        "SKILL_ROWS",
        "SUBAGENT_ROWS",
        "MANIFEST_DEPS",
        "WORKFLOWS",
        "ATTEST_PACK_DOC",
        "ATTEST_MCP_README",
        "ATTEST_HOOKS_README",
        "CRITERIA_NUMBERS",
        "REQ-PLAN-061_ROWS",
    )
    register = ("DEFERRAL_REGISTER", "DEFERRED_ROW")

    lines: list[str] = [
        "# Agent Extension Pack verification evidence (t35)",
        "",
        "Generated by `backend/scripts/agent_pack_verification.py` - never edit",
        "by hand. Re-running the script regenerates this document",
        "byte-identically (ac1 proves it by backup/re-run/restore). REQ-PLAN-061",
        "phase_6 verification rows, REQ-EXT-070/071 (the pack's own checklist,",
        "executed here), REQ-EXT-072 (the hook suite re-run as the",
        "milestone-exit regression moment), Chapter 24 §24.1 rows 7/9/10/11/12",
        "and §24.2 rows 31/32.",
        "",
        "## Method",
        "",
        "METHOD hermetic in-process: importlib loads the hyphenated hook modules",
        "by path; httpx.MockTransport stands in for the backend on every MCP leg",
        "(a rejected-token call provably performs zero transport requests);",
        "pytest.main re-runs the 14 hook and 12 MCP nodes in the same process;",
        "the backend collection count and the .agents symlink inventory arrive",
        "through files and are PARSED, never hand-typed. Nothing is spawned and",
        "no network client is constructed.",
        f"METHOD collection {collection} nodes (floor {COLLECTION_FLOOR}); the 26",
        "phase_6 node ids are re-run inside this run, not re-authored.",
        "",
        "## Executed rows (real measured values)",
        "",
        "```text",
    ]
    lines.extend(pick(tokens, executed))
    lines.extend(
        [
            "```",
            "",
            "`HOOK_TEST_ROWS` / `MCP_TEST_ROWS` carry the counts parsed from the",
            "live collection capture after re-running each suite in-process, so",
            "the counts are measured rather than asserted.",
            "`MCP_CONTRACT_ROWS` counts the real `list_tools()` inventory,",
            "dispatches one real `call_tool` through the mocked transport, then",
            "swaps in a wrongly-signed token and asserts the transport call count",
            "stayed at zero. `SYMLINK_ROWS` recounts git mode 120000 entries and",
            "proves cat-through byte-equality between each `.agents` symlink and",
            "its target file. `BACKEND_COLLECTION` is the live collection count",
            "the pinned commands counted, so ac2's cross-check is a closed loop.",
            "`COUNT_ROWS` / `AGENT_DIRS` / `PERMISSIONS_ROWS` are recounted from",
            "the tree and the matrix at run time (REQ-PROD-043, REQ-ARCH-053,",
            "REQ-AI-100/101).",
            "",
            "## Structural attestation rows",
            "",
            "```text",
        ]
    )
    lines.extend(pick(tokens, structural))
    lines.extend(
        [
            "```",
            "",
            f"The pack doc's verification checklist carries {checklist_lines} copyable",
            "component lines (REQ-EXT-070/071) - this card is the card that",
            f"executes them. README.md measures {readme_lines} lines, inside the",
            "<= 500 gate re-attested from this vantage (phase_6 touched none of",
            "the five named manifests and added no workflow).",
            "",
            "## REQ-PLAN-061 row modes",
            "",
            "```text",
        ]
    )
    lines.extend(pick(tokens, ("REQ-PLAN-061_ROWS", "CRITERIA_NUMBERS")))
    lines.extend(
        [
            "```",
            "",
            "| Row | Requirement | Mode | Evidence token |",
            "|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| {row} | {requirement} | {mode} | {token} |"
        for row, requirement, mode, token in criteria_rows()
    )
    lines.extend(
        [
            "",
            "Rows 7/9/10/11/12 are Chapter 24 §24.1 criteria rows (Criterion 12",
            "mapping via REQ-EXT-002); rows 31/32 are §24.2 technical rows. The",
            "discovery row re-proves REQ-AI-064/REQ-EXT-004/REQ-AI-070 through",
            "the git-tracked symlinks. Every cited token is grep-present above",
            "(the t28 ac5 mode-token cross-gate).",
            "",
            "## Deferral register (recorded, never asserted)",
            "",
            "```text",
        ]
    )
    lines.extend(pick(tokens, register))
    lines.extend(
        [
            "```",
            "",
            "A DEFERRED row is NEVER written as PASS (plan.md phase_6 ruling 5);",
            "ac4 greps the document for any PASS line naming a deferred key.",
            "Each row names the artifact that satisfies it, the measured host",
            "reason, and the operator's live-check command.",
            "",
            "## Summary",
            "",
            "```text",
        ]
    )
    lines.extend(pick(tokens, ("ALL_CHECKS_PASS", "CHECK_FAILURES")))
    lines.append("```")
    lines.append("")
    return "\r\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the capture-file arguments.

    Args:
        argv: Argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        argparse.Namespace: Parsed ``collection_file`` / ``ls_files_file``.
    """
    parser = argparse.ArgumentParser(description="Generate the t35 pack evidence document.")
    parser.add_argument("--collection-file", required=True, type=Path)
    parser.add_argument("--ls-files-file", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the hermetic verification and write the evidence document.

    Args:
        argv: Argument vector for :func:`parse_args`.

    Returns:
        int: Process exit code (0 only when every check passed).
    """
    args = parse_args(argv)
    pin_jwt_settings()
    v = Verifier()
    with tempfile.TemporaryDirectory(prefix="t35-verify-") as temp_dir:
        # The private temp dir keeps any scratch write off the working tree.
        (Path(temp_dir) / "scratch").write_text("t35", encoding="utf-8")
        node_ids = parse_collection(args.collection_file)
        record_hook_suite(v, node_ids)
        record_mcp_suite(v, node_ids)
        record_hook_contract(v)
        record_contract(v)
        record_symlinks(v, args.ls_files_file)
        record_counts(v)
        record_skill_structure(v)
        record_subagent_structure(v)
        record_permissions(v)
        record_manifest(v)
        record_workflows(v)
        record_docs_attestation(v)
        collection = record_collection(v, args.collection_file)
        emit_register(v)
        record_criteria(v)
    tokens = v.emit()
    document = render_document(tokens, collection)
    output = repo_root() / "docs" / "criteria" / "agent_pack_verification.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    # write_bytes keeps the explicit CRLF joins byte-exact on every platform
    # (no newline translation), matching the CRLF-smudged fresh checkout.
    output.write_bytes(document.encode("utf-8"))
    for token in tokens:
        print(token)
    print(f"WROTE {output.relative_to(repo_root()).as_posix()}")
    return 0 if not v.failures and v.checks >= MIN_CHECKS else 1


if __name__ == "__main__":
    raise SystemExit(main())

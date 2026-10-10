#!/usr/bin/env python
"""Hermetic infra verification run for t28 (REQ-PLAN-051 milestone exit).

This script is the verification deliverable of issue t28: it executes the
hermetically-executable milestone-exit rows (both live health states over
``create_app`` plus the SQLite-fallback timing, table, seed and no-Alembic
evidence), PARSES every structural attestation from the REAL infrastructure
files (Dockerfile / docker-compose.yml / .github/workflows/*.yml /
render.yaml / e2e/), maps the criteria/technical rows one line per row, and
GENERATES ``docs/criteria/infra_verification.md`` (t23 convention: pinned
CHECK/ATTEST/DEFER token lines with real measured values).

Hermetic by construction (plan.md phase_5 rulings 1/3/5):

* NO live server: ``fastapi.testclient.TestClient`` over ``create_app()``.
* The healthy run uses a PRIVATE sqlite file in a temporary directory
  wired in through ``dependency_overrides[get_db]``; the schema comes
  from ``Base.metadata.create_all`` (NOT alembic).
* The fallback run follows the t25 recipe exactly: the pinned unroutable
  primary ``postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe`` (closed
  loopback port, no egress) inside a private cwd, the latched flag reset,
  and the real startup handler performing the fallback initialization.
* Timing is RECORDED via ``time.perf_counter`` (``total_seconds`` scale) —
  never slept — and the ``DB_CONNECT_TIMEOUT`` budget is enforced here.
* NO subprocess, NO requests, NO uvicorn: the host facts behind the
  deferrals (docker daemon socket absent, docker/gh binaries absent) are
  measured with ``shutil.which`` and ``Path.exists`` only.
* Every structural count is PARSED (PyYAML / regex) from the real files —
  never hand-typed — so a drift between this document and the merged
  infrastructure fails the run.

The emitted PASS/DEFERRED evidence lines are deterministic apart from the
single recorded ``FALLBACK_WITHIN_5S elapsed=`` value, which is exactly the
inter-run delta ac1's byte-stability leg normalizes. The document ends
``ALL_CHECKS_PASS <N> PASS`` and the process exits 0 only when every check
passed and N >= MIN_CHECKS.

Usage (from ``backend/``):

    PYTHONPATH=. uv run python scripts/infra_verification.py
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app import database
from app.config import get_settings
from app.database import (
    DB_CONNECT_TIMEOUT,
    FALLBACK_DATABASE_URL,
    create_session_factory,
    get_db,
    is_fallback,
)
from app.main import create_app
from app.models import Base

JWT_SECRET = "t28-hermetic-infra-verification-secret-not-a-real-key"
"""Throwaway secret pinned for the hermetic run (never a real key)."""

PRIMARY_URL = "postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe"
"""The pinned unroutable primary (t25 recipe: closed loopback port)."""

EXPECTED_TABLES = ("users", "categories", "expenses", "budgets", "audit_logs")
EXPECTED_HEALTH_FIELDS = ("status", "database", "fallback_active", "version")
EXPECTED_SEEDED_CATEGORIES = 10
EXPECTED_WORKFLOWS = ("ci", "e2e", "deploy")
MIN_CHECKS = 20
"""Floor for the ALL_CHECKS_PASS total (t23 precedent scale, ac1 gate)."""

SCAN_TOKENS = ("codeql", "snyk", "trivy", "semgrep", "dependabot")
"""Banned security-scan tokens (phase_7 territory; ac3 pins the count 0)."""


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
            name: Token name (HEALTH_STATE_ROWS, DOCKERFILE_STAGES, ...).
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
            key: Register key (DOCKER_BUILD, COMPOSE_UP, ...).
            artifact: Repository artifact that satisfies the row.
            reason: Measured host reason (daemon_npipe_absent, ...).
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


def reset_fallback_state() -> None:
    """Clear the latched fallback flag and settings cache (t25 leak guard)."""
    database.IS_FALLBACK = False
    get_settings.cache_clear()


def pin_jwt_settings() -> None:
    """Pin JWT settings so the hermetic run never depends on `.env`."""
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "1440"
    os.environ["JWT_ISSUER"] = "expense-tracker"
    os.environ["JWT_AUDIENCE"] = "expense-tracker-api"
    reset_fallback_state()


def read_text(path: Path) -> str:
    """Read a repository file as UTF-8 text.

    Args:
        path: File to read.

    Returns:
        str: The file contents.
    """
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    """Parse a repository YAML file into a mapping.

    Args:
        path: YAML file to parse.

    Returns:
        dict[str, Any]: The parsed mapping.

    Raises:
        RuntimeError: When the document is not a mapping.
    """
    parsed: Any = yaml.safe_load(read_text(path))
    if not isinstance(parsed, dict):
        msg = f"{path.name} did not parse to a mapping"
        raise RuntimeError(msg)
    return parsed


def workflow_triggers(doc: dict[str, Any]) -> str:
    """Return the ``+``-joined trigger names of one workflow document.

    Args:
        doc: Parsed workflow YAML mapping.

    Returns:
        str: Trigger names in sorted order (e.g. ``pull_request+push``).
    """
    raw: dict[Any, Any] = dict(doc)
    on: Any = raw.get("on", raw.get(True))
    if isinstance(on, dict):
        return "+".join(sorted(str(name) for name in on))
    return str(on)


def healthy_run(temp_dir: str) -> dict[str, Any]:
    """Execute the healthy health state over a private sqlite database.

    Args:
        temp_dir: Directory holding the private sqlite files.

    Returns:
        dict[str, Any]: Status code and health body of the healthy run.
    """
    reset_fallback_state()
    healthy_db = (Path(temp_dir) / "t28_healthy.db").as_posix()
    engine = database.create_db_engine(f"sqlite:///{healthy_db}")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    def override() -> Generator[Session, None, None]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    startup_db = (Path(temp_dir) / "t28_startup.db").as_posix()
    os.environ["DATABASE_URL"] = f"sqlite:///{startup_db}"
    get_settings.cache_clear()
    application = create_app()
    application.dependency_overrides[get_db] = override
    with TestClient(application) as client:
        response = client.get("/api/v1/health")
        body: dict[str, Any] = response.json()
        status_code: int = response.status_code
    return {"status_code": status_code, "body": body}


def fallback_run(temp_dir: str) -> dict[str, Any]:
    """Execute the t25 fallback path and measure its evidence.

    Args:
        temp_dir: Private cwd for the run (``fallback.db`` lands here).

    Returns:
        dict[str, Any]: Measured elapsed, health body, tables, seed count,
            latched flag, engine URL and the Alembic-import fact.
    """
    reset_fallback_state()
    previous_cwd = Path.cwd()
    os.chdir(temp_dir)
    os.environ["DATABASE_URL"] = PRIMARY_URL
    get_settings.cache_clear()
    application = create_app()
    client = TestClient(application)
    try:
        started = time.perf_counter()
        client.__enter__()
        elapsed = time.perf_counter() - started
        try:
            response = client.get("/api/v1/health")
            body: dict[str, Any] = response.json()
            status_code: int = response.status_code
            latched = is_fallback()
            engine_url = str(application.state.db_engine.url)
            fallback_db = (Path(temp_dir) / "fallback.db").as_posix()
            probe = database.create_db_engine(f"sqlite:///{fallback_db}")
            names = set(inspect(probe).get_table_names())
            tables = [name for name in EXPECTED_TABLES if name in names]
            with probe.connect() as conn:
                seeded = int(
                    conn.exec_driver_sql(
                        "SELECT COUNT(*) FROM categories WHERE user_id IS NULL"
                    ).scalar()
                    or 0
                )
        finally:
            client.__exit__(None, None, None)
    finally:
        os.chdir(previous_cwd)
        reset_fallback_state()
    return {
        "elapsed": elapsed,
        "status_code": status_code,
        "body": body,
        "tables": tables,
        "seeded": seeded,
        "latched": latched,
        "engine_url": engine_url,
        "alembic_imported": "alembic" in sys.modules,
    }


def measure_host_facts() -> dict[str, bool]:
    """Measure the subprocess-free host facts behind the deferrals.

    Returns:
        dict[str, bool]: Measured facts (True means the capability is
            absent on this host).
    """
    npipe = Path("\\\\.\\pipe\\dockerDesktopLinuxEngine")
    socket = Path("/var/run/docker.sock")
    return {
        "daemon_npipe_absent": not (npipe.exists() or socket.exists()),
        "docker_cli_absent": shutil.which("docker") is None,
        "gh_absent": shutil.which("gh") is None,
    }


def record_executed(v: Verifier, healthy: dict[str, Any], degraded: dict[str, Any]) -> None:
    """Record the six executed health/fallback evidence tokens.

    Args:
        v: The token ledger.
        healthy: Measured healthy-path run results.
        degraded: Measured fallback-path run results.
    """
    ok_body: dict[str, Any] = healthy["body"]
    deg_body: dict[str, Any] = degraded["body"]
    healthy_ok = (
        healthy["status_code"] == 200
        and ok_body.get("status") == "ok"
        and ok_body.get("database") == "sqlite"
        and ok_body.get("fallback_active") is False
    )
    degraded_ok = (
        degraded["status_code"] == 200
        and deg_body.get("status") == "degraded"
        and deg_body.get("database") == "sqlite"
        and deg_body.get("fallback_active") is True
    )
    states = "ok/sqlite/false degraded/sqlite/true"
    v.record("HEALTH_STATE_ROWS", healthy_ok and degraded_ok, states)
    fields_ok = sorted(str(key) for key in ok_body) == sorted(EXPECTED_HEALTH_FIELDS)
    v.record(
        "HEALTH_FIELDS",
        fields_ok,
        ",".join(EXPECTED_HEALTH_FIELDS) if fields_ok else ",".join(sorted(ok_body)),
    )
    tables = list(degraded["tables"])
    v.record("FALLBACK_TABLES", tables == list(EXPECTED_TABLES), ",".join(tables))
    seeded = int(degraded["seeded"])
    v.record("FALLBACK_SEEDED_CATEGORIES", seeded == EXPECTED_SEEDED_CATEGORIES, str(seeded))
    alembic_imported = bool(degraded["alembic_imported"])
    v.record("FALLBACK_NO_ALEMBIC_IMPORT", not alembic_imported, "alembic=absent")
    elapsed = float(degraded["elapsed"])
    within = (
        elapsed < DB_CONNECT_TIMEOUT
        and bool(degraded["latched"])
        and degraded["engine_url"] == FALLBACK_DATABASE_URL
    )
    v.record("FALLBACK_WITHIN_5S", within, f"elapsed={elapsed:.3f} bound={DB_CONNECT_TIMEOUT}")


def parse_dockerfile(root: Path, v: Verifier) -> None:
    """Parse the Dockerfile stage tags and the migration CMD leg.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    text = read_text(root / "Dockerfile")
    stages = re.findall(r"(?m)^FROM\s+(\S+)", text)
    v.record("DOCKERFILE_STAGES", len(stages) == 2, " ".join([str(len(stages)), *stages]))
    cmd_line = re.search(r"(?m)^CMD\s+\[.*\]", text)
    migrated = bool(cmd_line and re.search(r"alembic upgrade head", cmd_line.group(0)))
    v.record("DOCKERFILE_CMD", migrated, "alembic upgrade head" if migrated else "missing")


def parse_compose(root: Path, v: Verifier) -> None:
    """Parse the compose services, healthchecks, volume and port mapping.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    compose = load_yaml(root / "docker-compose.yml")
    services: dict[str, Any] = compose.get("services", {})
    names = list(services)
    healthchecks = sum(1 for spec in services.values() if "healthcheck" in spec)
    volumes = list(compose.get("volumes", {}))
    ports = [str(mapping) for spec in services.values() for mapping in spec.get("ports", [])]
    v.record(
        "COMPOSE_SERVICES",
        sorted(names) == ["app", "db"],
        f"{','.join(names)} {len(names)}",
    )
    v.record("COMPOSE_HEALTHCHECKS", healthchecks == 2, str(healthchecks))
    v.record("COMPOSE_VOLUME", volumes == ["db_data"], ",".join(volumes))
    v.record("COMPOSE_PORT_MAPPING", "8000:8000" in ports, ";".join(ports))


def parse_workflows(root: Path, v: Verifier) -> None:
    """Parse the workflow set, trigger matrix and runner flags.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    workflow_dir = root / ".github" / "workflows"
    docs = {path.stem: load_yaml(path) for path in sorted(workflow_dir.glob("*.yml"))}
    names = sorted(docs)
    ordered = sorted(names, key=lambda name: EXPECTED_WORKFLOWS.index(name)) if (
        set(names) == set(EXPECTED_WORKFLOWS)
    ) else names
    v.record(
        "WORKFLOWS",
        set(names) == set(EXPECTED_WORKFLOWS),
        f"{','.join(ordered)} {len(names)}",
    )
    triggers = {name: workflow_triggers(docs[name]) for name in names}
    expected = {"ci": "pull_request+push", "e2e": "push", "deploy": "workflow_run"}
    v.record(
        "WORKFLOW_TRIGGERS",
        all(triggers.get(name) == expected[name] for name in expected),
        " ".join(f"{name}={triggers.get(name)}" for name in EXPECTED_WORKFLOWS),
    )
    concurrency = sum(
        1
        for doc in docs.values()
        if isinstance(doc.get("concurrency"), dict)
        and doc["concurrency"].get("cancel-in-progress") is True
    )
    caching = False
    for doc in docs.values():
        for job in doc.get("jobs", {}).values():
            for step in job.get("steps", []):
                with_args = step.get("with") if isinstance(step, dict) else None
                if isinstance(with_args, dict) and (
                    with_args.get("enable-cache") is True or "cache" in with_args
                ):
                    caching = True
    scanned = sum(
        1
        for name in names
        for token in SCAN_TOKENS
        if token in read_text(workflow_dir / f"{name}.yml").lower()
    )
    v.record(
        "WORKFLOW_FLAGS",
        concurrency == 2 and caching and scanned == 0,
        f"concurrency={concurrency} caching={'enabled' if caching else 'disabled'} "
        f"security_scans={scanned}",
    )


def parse_render(root: Path, v: Verifier) -> None:
    """Parse the Render blueprint services, health path and env keys.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    blueprint = load_yaml(root / "render.yaml")
    services: list[Any] = blueprint.get("services", [])
    databases: list[Any] = blueprint.get("databases", [])
    web: dict[str, Any] = services[0] if services else {}
    env_keys = [str(entry.get("key", "")) for entry in web.get("envVars", [])]
    token = ",".join([str(web.get("type"))] + (["db"] if databases else []))
    v.record(
        "RENDER_SERVICE",
        len(services) == 1 and len(databases) == 1 and web.get("type") == "web",
        token,
    )
    v.record(
        "RENDER_HEALTH_CHECK_PATH",
        web.get("healthCheckPath") == "/api/v1/health",
        str(web.get("healthCheckPath")),
    )
    v.record("RENDER_ENV_KEYS", len(env_keys) == 9, str(len(env_keys)))


def parse_e2e(root: Path, v: Verifier) -> None:
    """Parse the Playwright workspace artifacts and pinned numerics.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    e2e = root / "e2e"
    configs = len(list(e2e.glob("playwright.config.ts")))
    fixtures = len(list((e2e / "fixtures").glob("*.ts")))
    specs = len(list((e2e / "tests").glob("*.spec.ts")))
    v.record(
        "E2E_ARTIFACTS",
        configs == 1 and fixtures == 2 and specs == 3,
        f"config={configs} fixtures={fixtures} specs={specs}",
    )
    config_text = read_text(e2e / "playwright.config.ts")

    def config_number(key: str) -> int:
        match = re.search(rf"(?m)^\s*{key}:\s*[0-9_]+\s*,", config_text)
        if match is None:
            return -1
        digits = re.search(r"[0-9_]+", match.group(0))
        return int(digits.group(0).replace("_", "")) if digits else -1

    timeout = config_number("timeout")
    retries = config_number("retries")
    workers = config_number("workers")
    v.record(
        "E2E_CONFIG_NUMBERS",
        timeout == 60000 and retries == 1 and workers == 1,
        f"timeout={timeout} retries={retries} workers={workers}",
    )


def attest_readme(root: Path, v: Verifier) -> None:
    """Attest the README cold-start note and UptimeRobot text artifacts.

    Args:
        root: Repository root.
        v: The token ledger.
    """
    readme = read_text(root / "README.md")
    v.record("ATTEST_README_COLD_START_NOTE", "cold start" in readme, "PRESENT")
    v.record("ATTEST_UPTIMEROBOT_TEXT", "UptimeRobot" in readme, "PRESENT")


def criteria_rows() -> list[tuple[str, str, str, str]]:
    """Return the twelve pinned criteria/technical mapping rows.

    Returns:
        list[tuple[str, str, str, str]]: (row, requirement, mode, token).
    """
    return [
        ("29", "REQ-OPS-011", "executed", "HEALTH_STATE_ROWS"),
        ("30", "REQ-PROD-017", "executed", "FALLBACK_WITHIN_5S"),
        ("5", "REQ-TECH-041", "deferred", "DEFERRED_ROW COMPOSE_UP"),
        ("6", "REQ-TECH-042", "deferred", "DEFERRED_ROW DOCKER_BUILD"),
        ("7", "REQ-CICD-011", "structural", "WORKFLOWS"),
        ("8", "REQ-CICD-012", "structural", "WORKFLOW_TRIGGERS"),
        ("9", "REQ-CICD-013", "structural", "WORKFLOW_TRIGGERS"),
        ("12", "REQ-OPS-012", "executed", "HEALTH_FIELDS"),
        ("13", "REQ-PROD-017", "executed", "FALLBACK_WITHIN_5S"),
        ("16", "REQ-CICD-001", "structural", "WORKFLOWS"),
        ("17", "REQ-CICD-036", "deferred", "DEFERRED_ROW RENDER_DEPLOY"),
        ("18", "REQ-DB-082", "structural", "DOCKERFILE_CMD"),
    ]


def record_criteria(v: Verifier) -> None:
    """Record the criteria-numbers header gated by the token cross-check.

    Args:
        v: The token ledger.
    """
    cited = all(
        any(token.startswith(tok) for token in v.tokens)
        for _, _, _, tok in criteria_rows()
    )
    v.record("CRITERIA_NUMBERS", cited, "8,10,11")


def emit_register(v: Verifier, facts: dict[str, bool]) -> None:
    """Emit the seven-row deferral register (recorded, never asserted).

    Args:
        v: The token ledger.
        facts: Measured subprocess-free host facts.
    """
    daemon_reason = "daemon_npipe_absent" if facts["daemon_npipe_absent"] else "daemon_present"
    actions_reason = "actions_untriggerable" if facts["gh_absent"] else "actions_reachable"
    v.tokens.append("DEFERRAL_REGISTER 7 DEFERRED")
    v.defer(
        "DOCKER_BUILD",
        "Dockerfile",
        daemon_reason,
        "docker build -t expense-tracker-dashboard:verify .",
    )
    v.defer(
        "COMPOSE_UP",
        "docker-compose.yml",
        daemon_reason,
        "docker compose up -d --build && curl -fsS http://localhost:8000/api/v1/health",
    )
    v.defer(
        "CI_PR_RUN",
        ".github/workflows/ci.yml",
        actions_reason,
        "gh run list --workflow=ci.yml --limit 5",
    )
    v.defer(
        "E2E_RUN",
        "e2e/playwright.config.ts",
        actions_reason,
        "gh run list --workflow=e2e.yml --limit 5",
    )
    v.defer(
        "RENDER_DEPLOY",
        "render.yaml",
        "egress_forbidden",
        "curl -fsS https://api.render.com/v1/services/srv-REPLACE_ME/deploys",
    )
    v.defer("UPTIMEROBOT_MONITOR", "README.md", "egress_forbidden", "uptime checks get --all")
    v.defer(
        "LIVE_COLD_START",
        "README.md",
        "egress_forbidden",
        "curl -o /dev/null -s -w '%{time_total}' "
        "https://expense-tracker-dashboard.onrender.com/api/v1/health after an idle gap, "
        "gated against the 60s REQ-PROD-020 Should",
    )


def render_document(tokens: list[str], facts: dict[str, bool]) -> str:
    """Render the criteria evidence document from the token ledger.

    Args:
        tokens: The token ledger (in emit order).
        facts: Measured subprocess-free host facts.

    Returns:
        str: The full document text with CRLF newlines.
    """

    def section(prefixes: tuple[str, ...]) -> list[str]:
        return [token for token in tokens if token.startswith(prefixes)]

    lines: list[str] = [
        "# Infra verification evidence (t28)",
        "",
        "Generated by `backend/scripts/infra_verification.py` - never edit by",
        "hand. Re-running the script regenerates this document byte-identically",
        "across every PASS/DEFERRED evidence line (ac1 proves it by",
        "backup/re-run/restore; the recorded elapsed timing is the only",
        "permitted inter-run delta). Phase 5 milestone-exit verification:",
        "criteria 8/10/11 (REQ-CICD-001), criteria rows 29/30, technical rows",
        "5/6/7/8/9/12/13/16/17/18, and the REQ-PLAN-051 executed-or-deferred",
        "ruling (plan.md phase_5 rulings 1/3/5).",
        "",
        "## Method",
        "",
        "METHOD hermetic TestClient over create_app; the healthy path runs on a",
        "private sqlite file via a get_db dependency override; the fallback path",
        "runs on the pinned unroutable primary",
        "postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe with the real",
        "startup handler performing the t25 fallback initialization (t25 W7a",
        "contract: DB_CONNECT_TIMEOUT and FALLBACK_DATABASE_URL imported from",
        "app.database, is_fallback latched by the probe). Timing is recorded via",
        "time.perf_counter (total_seconds scale), never slept. No live server,",
        "no docker, no subprocess, no requests, no uvicorn.",
        f"METHOD host daemon_socket={'absent' if facts['daemon_npipe_absent'] else 'present'}",
        f"gh_cli={'absent' if facts['gh_absent'] else 'present'}.",
        "",
        "## Executed health and fallback evidence (criteria rows 29/30, technical rows 12/13)",
        "",
        "Both live health states are executed through TestClient (REQ-OPS-011,",
        "REQ-OPS-012); the fallback timing, table list, seeded-category count",
        "and no-Alembic fact are measured on the real startup fallback path",
        "(REQ-PROD-017, REQ-DB-083, FR-DB-1).",
        "",
        "```text",
    ]
    lines.extend(section(("HEALTH_", "FALLBACK_")))
    lines.extend(
        [
            "```",
            "",
            "The fallback schema arrives via create_all plus the merged seed",
            "routine, never through Alembic (REQ-DB-083); the ten system",
            "categories are seeded on the fallback path (REQ-PROD-013); the",
            "elapsed value above is the real measured startup duration gated",
            "against the 5-second budget (REQ-BE-130).",
            "",
            "## Structural attestations (script-parsed from the real files)",
            "",
            "The Dockerfile, docker-compose.yml, .github/workflows/*.yml,",
            "render.yaml and e2e/ counts below are PARSED at run time (PyYAML",
            "and regex), never hand-typed: a drift between the merged",
            "infrastructure and this document fails the run (technical rows 5-9,",
            "16, 18; REQ-CICD-032, REQ-TEST-040, REQ-DB-082).",
            "",
            "```text",
        ]
    )
    lines.extend(section(("DOCKERFILE_", "COMPOSE_", "WORKFLOW", "RENDER_", "E2E_")))
    lines.extend(
        [
            "```",
            "",
            "## Deferral register (plan.md phase_5 ruling 5 - recorded, never asserted)",
            "",
            "Every row this host cannot execute is recorded with the artifact that",
            "satisfies it, the measured host reason (daemon npipe absent, GitHub",
            "Actions untriggerable, network egress forbidden) and the operator's",
            "live-check command. A deferred row is NEVER written as PASS.",
            "",
            "```text",
        ]
    )
    lines.extend(section(("DEFERRAL_REGISTER", "DEFERRED_ROW", "ATTEST_")))
    lines.extend(
        [
            "```",
            "",
            "## Criteria mapping (REQ-CICD-001 - criteria 8,10,11)",
            "",
            "```text",
        ]
    )
    lines.extend(section(("CRITERIA_NUMBERS",)))
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
            "Rows 29/30 are the Chapter 24 §24.1 criteria rows; rows 5/6/7/8/9/",
            "12/13/16/17/18 are the §24.2 technical acceptance rows. REQ-PLAN-051",
            "is satisfied as executed-or-deferred per row (ruling 5); the",
            "REQ-TECH-062/REQ-CICD-041 UptimeRobot Should is attested as an",
            "artifact (the README text) with the live monitor deferred.",
            "",
            "```text",
        ]
    )
    lines.extend(section(("ALL_CHECKS_PASS", "CHECK_FAILURES")))
    lines.append("```")
    lines.append("")
    return "\r\n".join(lines)


def main() -> int:
    """Run the hermetic verification and write the evidence document.

    Returns:
        int: Process exit code (0 only when every check passed).
    """
    repo_root = Path(__file__).resolve().parents[2]
    pin_jwt_settings()
    v = Verifier()
    with tempfile.TemporaryDirectory(prefix="t28-verify-") as temp_dir:
        healthy = healthy_run(temp_dir)
        degraded = fallback_run(temp_dir)
        facts = measure_host_facts()
        record_executed(v, healthy, degraded)
        parse_dockerfile(repo_root, v)
        parse_compose(repo_root, v)
        parse_workflows(repo_root, v)
        parse_render(repo_root, v)
        parse_e2e(repo_root, v)
        attest_readme(repo_root, v)
        emit_register(v, facts)
        record_criteria(v)
    tokens = v.emit()
    document = render_document(tokens, facts)
    output = repo_root / "docs" / "criteria" / "infra_verification.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8", newline="")
    for token in tokens:
        print(token)
    print(f"WROTE {output.relative_to(repo_root).as_posix()}")
    return 0 if not v.failures and v.checks >= MIN_CHECKS else 1


if __name__ == "__main__":
    raise SystemExit(main())

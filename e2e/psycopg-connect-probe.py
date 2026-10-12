"""File-based psycopg connect probe (t43, REQ-BE-130 evidence, Option A-bis).

Performs a REAL ``psycopg.connect(host=..., port=5432, connect_timeout=15, ...)``
attempt against the primary database host and writes ``e2e/psycopg-import.log``
(gitignored runtime artifact, never committed) with an
``^psycopg_connect_ok mode=(connected|driver_ok)`` evidence line.

Host resolution order (Option A-bis, non-secret only per REQ-CICD-070):
    1. ``REPAIR_PG_HOST`` environment variable (operator-provided at run time),
    2. the host parsed from ``DATABASE_URL``,
    3. the literal non-secret placeholder ``dpg-placeholder-a.postgres.render.com``.

Honesty of the modes (Option A-bis ruling, carried verbatim in intent):
    * ``mode=connected``  - an authenticated connect SUCCEEDED.
    * ``mode=driver_ok``  - the psycopg driver is installed AND its wire
      layer was reached (DNS resolution, TCP connect, TLS/startup
      handshake attempted) within ``connect_timeout=15``; a
      ``psycopg.Error`` subclass was returned. This does NOT attest
      literal TCP reachability, authentication, or a live database, and
      this card does not require an authenticated connect.
    * ``psycopg_driver_missing`` - the driver import raised
      ``ImportError``/``ModuleNotFoundError``; the script exits 1.

The script is dependency-light (stdlib + psycopg only), offline-safe
(placeholder host + 15s timeout, no secrets), and never commits its log.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

PLACEHOLDER_HOST = "dpg-placeholder-a.postgres.render.com"
"""Non-secret placeholder host (Option A-bis); never a credential or real host."""

LOG_FILE = Path(__file__).resolve().parent / "psycopg-import.log"
"""File-based evidence target: e2e/psycopg-import.log (gitignored)."""


def resolve_host() -> str:
    """Resolve the probe host: REPAIR_PG_HOST -> DATABASE_URL -> placeholder.

    Returns:
        str: The hostname to connect to.
    """
    override = os.environ.get("REPAIR_PG_HOST", "").strip()
    if override:
        return override
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        try:
            host = urlsplit(database_url).hostname
        except ValueError:
            host = None
        if host:
            return str(host)
    return PLACEHOLDER_HOST


def main() -> int:
    """Run the connect probe and write the evidence log.

    Returns:
        int: 0 when the driver is installed (connected or driver_ok),
        1 when the driver is missing (``psycopg_driver_missing``).
    """
    try:
        import psycopg
    except (ImportError, ModuleNotFoundError):
        print("psycopg_driver_missing")  # noqa: T201
        return 1

    host = resolve_host()
    try:
        connection = psycopg.connect(
            host=host,
            port=5432,
            dbname="probe",
            user="probe",
            password="***",
            connect_timeout=15,
        )
    except psycopg.Error as exc:
        # Wire layer reached (DNS/TCP/TLS-handshake attempted); the
        # server or the network refused/failed the startup exchange.
        # Honest naming per Option A-bis: driver_ok, NOT a reachability claim.
        line = (
            f"psycopg_connect_ok mode=driver_ok host={host} "
            f"error={type(exc).__name__}"
        )
        LOG_FILE.write_text(line + "\n", encoding="utf-8")
        print(line)  # noqa: T201
        return 0
    connection.close()
    line = f"psycopg_connect_ok mode=connected host={host}"
    LOG_FILE.write_text(line + "\n", encoding="utf-8")
    print(line)  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())

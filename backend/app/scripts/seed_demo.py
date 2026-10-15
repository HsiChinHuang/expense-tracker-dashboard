"""Idempotent demo-account seed for the README live demo (t65).

Population-only script: it adds NO schema, NO endpoint and NO
dependency. It writes the fixed demo account (``demo@example.com`` /
``demo-password-123``, hashed through the merged bcrypt primitive)
plus a deterministic ~90-day expense dataset and one budget per
covered month, reusing the merged system-category seed routine
(:func:`app.scripts.seed.seed_system_categories`) — ``seed.py`` and
the Alembic revision that pre-seeds the ten categories are frozen.

Idempotency contract (wipe + rebuild): :func:`wipe_demo_data` deletes
ONLY the demo account's own expenses, budgets, audit rows and the demo
user row, then :func:`seed_demo_data` regenerates the dataset. Rows of
any other user and the shared system categories (``user_id`` NULL) are
never touched. Both helpers are Core-only and NEVER commit —
:func:`main` owns the engine and the transaction.

Determinism contract: generation is a pure function of the day offset
from the anchor (:func:`_resolve_anchor`, default ``date.today()``,
overridable via ``SEED_DEMO_ANCHOR=YYYY-MM-DD``). Row content depends
only on the offset and the seeded RNG stream, never on absolute
dates, so the same anchor reproduces the dataset byte-for-byte and
different anchors produce the same (offset, category, amount) set.
Money is ``Decimal`` quantized to exactly 2 decimal places end to end.
"""

import os
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Final

import sqlalchemy as sa
from sqlalchemy.engine import Connection, Engine

from app.auth.password import hash_password
from app.config import get_settings
from app.database import create_db_engine
from app.scripts.seed import SYSTEM_CATEGORIES, seed_system_categories

DEMO_EMAIL: Final[str] = "demo@example.com"
"""The fixed demo account email the README live-demo section names."""

DEMO_PASSWORD: Final[str] = "demo-password-123"
"""The fixed demo account password (hashed, never stored in clear)."""

DEMO_USERNAME: Final[str] = "demo"
"""The fixed demo account username."""

SPAN_DAYS: Final[int] = 90
"""Number of consecutive days the demo dataset spans, ending at the anchor."""

RNG_SEED: Final[int] = 20261015
"""Fixed seed for the deterministic generation stream (t65 ac4/ac6)."""

ANCHOR_ENV_VAR: Final[str] = "SEED_DEMO_ANCHOR"
"""Environment variable overriding the anchor date (YYYY-MM-DD)."""

_TWO_DP: Final[Decimal] = Decimal("0.01")
"""Quantizer pinning every money value to exactly 2 decimal places."""

_BASE_WEIGHTS: Final[tuple[int, ...]] = (20, 10, 9, 6, 7, 8, 9, 6, 3, 13)
"""Per-category selection weights, aligned to SYSTEM_CATEGORIES order."""

_AMOUNT_RANGES: Final[tuple[tuple[str, str], ...]] = (
    ("8.50", "38.00"),
    ("12.00", "95.00"),
    ("4.50", "32.00"),
    ("850.00", "1450.00"),
    ("35.00", "160.00"),
    ("9.00", "55.00"),
    ("15.00", "180.00"),
    ("18.00", "90.00"),
    ("65.00", "520.00"),
    ("20.00", "220.00"),
)
"""Per-category plausible [min, max] amount bounds as 2-dp strings."""

_NOTES: Final[tuple[str, ...]] = (
    "demo expense",
    "demo lunch",
    "demo transit fare",
    "demo groceries",
    "demo subscription",
    "demo household bill",
    "demo leisure",
    "demo shopping",
    "demo wellness",
    "demo trip",
    "demo misc",
)
"""Short plausible note pool for generated expenses."""

_budget_table = sa.table(
    "budgets",
    sa.column("id", sa.Uuid()),
    sa.column("user_id", sa.Uuid()),
    sa.column("year_month", sa.String(7)),
    sa.column("amount", sa.Numeric(12, 2)),
)
"""Core view of ``budgets`` — wipe/delete is scoped to the demo user."""

_expense_table = sa.table(
    "expenses",
    sa.column("id", sa.Uuid()),
    sa.column("user_id", sa.Uuid()),
    sa.column("category_id", sa.Uuid()),
    sa.column("amount", sa.Numeric(12, 2)),
    sa.column("currency", sa.String(3)),
    sa.column("date", sa.Date()),
    sa.column("note", sa.Text()),
)
"""Core view of ``expenses`` — wipe/delete is scoped to the demo user."""

_audit_table = sa.table(
    "audit_logs",
    sa.column("id", sa.Uuid()),
    sa.column("user_id", sa.Uuid()),
)
"""Core view of ``audit_logs`` — demo seeds write none, wipe clears any."""

_category_table = sa.table(
    "categories",
    sa.column("id", sa.Uuid()),
    sa.column("user_id", sa.Uuid()),
    sa.column("name", sa.String(100)),
    sa.column("is_system", sa.Boolean()),
)
"""Core view of ``categories`` — read-only here; wipe NEVER deletes it."""

_user_table = sa.table(
    "users",
    sa.column("id", sa.Uuid()),
    sa.column("email", sa.String(255)),
    sa.column("username", sa.String(50)),
    sa.column("hashed_password", sa.String(255)),
    sa.column("is_active", sa.Boolean()),
)
"""Core view of ``users`` — only the fixed demo row is inserted/deleted."""


def _resolve_anchor() -> date:
    """Resolve the generation anchor date.

    Returns:
        date: ``SEED_DEMO_ANCHOR`` (``YYYY-MM-DD``) when set, else
            ``date.today()``.
    """
    raw = os.environ.get(ANCHOR_ENV_VAR, "").strip()
    if raw:
        return date.fromisoformat(raw)
    return date.today()


def _month_keys(anchor: date) -> list[str]:
    """Return the sorted ``YYYY-MM`` keys the 90-day span touches.

    Args:
        anchor: Last day of the span.

    Returns:
        list[str]: Distinct month keys in ascending order.
    """
    months = {
        f"{day.year:04d}-{day.month:02d}"
        for day in (anchor - timedelta(days=offset) for offset in range(SPAN_DAYS))
    }
    return sorted(months)


def _generate_expense_rows(
    user_id: uuid.UUID, anchor: date, category_ids: dict[str, uuid.UUID]
) -> list[dict[str, Any]]:
    """Generate the deterministic 90-day demo expense rows.

    Row content is a pure function of the day offset and the seeded
    RNG stream: the same anchor always produces the same rows and any
    two anchors produce the same (offset, category, amount) triples.

    Args:
        user_id: Demo account id the rows will belong to.
        anchor: Last day of the span (day 89).
        category_ids: Mapping of system-category name to row id.

    Returns:
        list[dict[str, Any]]: Insert-ready expense rows.
    """
    rng = random.Random(RNG_SEED)
    names = [entry["name"] for entry in SYSTEM_CATEGORIES]
    rows: list[dict[str, Any]] = []
    for offset in range(SPAN_DAYS):
        day = anchor - timedelta(days=SPAN_DAYS - 1 - offset)
        count = 1 + rng.choices([0, 1, 2], weights=[25, 45, 30], k=1)[0]
        for _ in range(count):
            name = rng.choices(names, weights=list(_BASE_WEIGHTS), k=1)[0]
            index = names.index(name)
            low, high = (Decimal(value) for value in _AMOUNT_RANGES[index])
            amount = (low + (high - low) * Decimal(rng.random())).quantize(_TWO_DP)
            rows.append(
                {
                    "id": uuid.uuid4(),
                    "user_id": user_id,
                    "category_id": category_ids[name],
                    "amount": amount,
                    "currency": "USD",
                    "date": day,
                    "note": rng.choice(_NOTES),
                }
            )
    return rows


def _generate_budget_rows(
    user_id: uuid.UUID, anchor: date
) -> list[dict[str, Any]]:
    """Generate one plausible budget per month the span covers.

    Args:
        user_id: Demo account id the rows will belong to.
        anchor: Last day of the span.

    Returns:
        list[dict[str, Any]]: Insert-ready budget rows.
    """
    rng = random.Random(RNG_SEED + 1)
    return [
        {
            "id": uuid.uuid4(),
            "user_id": user_id,
            "year_month": month,
            "amount": (Decimal("1800") + Decimal(rng.randrange(0, 501))).quantize(
                _TWO_DP
            ),
        }
        for month in _month_keys(anchor)
    ]


def wipe_demo_data(bind: Connection) -> None:
    """Delete every row owned by the fixed demo account.

    Deletes the demo account's expenses, budgets and audit rows, then
    the demo user row. The shared system categories (``user_id`` NULL)
    are NEVER deleted — every account depends on them — and rows of
    any other user are never touched.

    Args:
        bind: A Core Connection owned by the caller. Never commits.
    """
    demo_ids = bind.execute(
        sa.select(_user_table.c.id).where(_user_table.c.email == DEMO_EMAIL)
    ).scalars().all()
    for demo_id in demo_ids:
        bind.execute(
            sa.delete(_expense_table).where(_expense_table.c.user_id == demo_id)
        )
        bind.execute(
            sa.delete(_budget_table).where(_budget_table.c.user_id == demo_id)
        )
        bind.execute(sa.delete(_audit_table).where(_audit_table.c.user_id == demo_id))
        bind.execute(sa.delete(_user_table).where(_user_table.c.id == demo_id))


def seed_demo_data(bind: Connection, anchor: date | None = None) -> dict[str, int]:
    """Wipe, then rebuild the fixed demo account and its dataset.

    Args:
        bind: A Core Connection owned by the caller. Never commits.
        anchor: Generation anchor; ``None`` resolves via
            :func:`_resolve_anchor`.

    Returns:
        dict[str, int]: Row counts keyed ``expenses`` / ``budgets``.
    """
    resolved = anchor if anchor is not None else _resolve_anchor()
    wipe_demo_data(bind)
    seed_system_categories(bind)
    category_ids: dict[str, uuid.UUID] = dict(
        bind.execute(
            sa.select(_category_table.c.name, _category_table.c.id).where(
                _category_table.c.user_id.is_(None)
            )
        ).all()
    )
    demo_id = uuid.uuid4()
    bind.execute(
        sa.insert(_user_table).values(
            id=demo_id,
            email=DEMO_EMAIL,
            username=DEMO_USERNAME,
            hashed_password=hash_password(DEMO_PASSWORD),
            is_active=True,
        )
    )
    expenses = _generate_expense_rows(demo_id, resolved, category_ids)
    budgets = _generate_budget_rows(demo_id, resolved)
    bind.execute(sa.insert(_expense_table), expenses)
    bind.execute(sa.insert(_budget_table), budgets)
    return {"expenses": len(expenses), "budgets": len(budgets)}


def main() -> None:
    """Run the demo seed against the effective configured database.

    The engine comes from the app settings, so a ``DATABASE_URL``
    override redirects the run at a probe database and the operator's
    ``dev.db`` stays untouched. The whole wipe+rebuild is one
    transaction owned here — the only place anything commits.
    """
    engine: Engine = create_db_engine(get_settings().DATABASE_URL)
    try:
        with engine.begin() as connection:
            counts = seed_demo_data(connection)
        print(
            "seed_demo: demo account ready "
            f"({DEMO_EMAIL} / {DEMO_PASSWORD}) — "
            f"{counts['expenses']} expenses, {counts['budgets']} budgets"
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

"""Idempotent system-category seed routine (REQ-DB-070/071/072).

Holds the ten Chapter 5 section 5.9.1 rows verbatim. The routine is
Core-only on purpose: it imports NO ORM model and NEVER commits (the
caller owns the transaction), which makes it safe to call from the
Alembic data step in revision ``002`` — the trigger pinned by ac4 (the
merged ``database.py`` has no create_all()/startup seam, so no app hook
exists; the §5.9.3 "SQLite tests" row is served by tests calling this
same function directly).
"""

import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine import Connection

SYSTEM_CATEGORIES: list[dict[str, str]] = [
    {"name": "Food & Dining", "color": "#EF4444", "icon": "utensils"},
    {"name": "Groceries", "color": "#F97316", "icon": "shopping-cart"},
    {"name": "Transportation", "color": "#EAB308", "icon": "car"},
    {"name": "Housing & Rent", "color": "#22C55E", "icon": "home"},
    {"name": "Utilities", "color": "#14B8A6", "icon": "zap"},
    {"name": "Entertainment", "color": "#3B82F6", "icon": "film"},
    {"name": "Shopping", "color": "#8B5CF6", "icon": "bag"},
    {"name": "Health & Fitness", "color": "#EC4899", "icon": "heart"},
    {"name": "Travel", "color": "#06B6D4", "icon": "plane"},
    {"name": "Other", "color": "#6B7280", "icon": "more-horizontal"},
]
"""The pinned ten system categories of Chapter 5 section 5.9.1."""

_categories = sa.table(
    "categories",
    sa.column("id", sa.Uuid()),
    sa.column("user_id", sa.Uuid()),
    sa.column("name", sa.String(100)),
    sa.column("color", sa.String(7)),
    sa.column("icon", sa.String(50)),
    sa.column("is_system", sa.Boolean()),
)


def seed_system_categories(bind: Connection) -> int:
    """Insert the ten system categories that are not present yet.

    Idempotent per REQ-DB-071: a category counts as present when a row
    with the same ``name`` and ``user_id IS NULL`` already exists, so a
    second run inserts nothing. Ids are generated in Python
    (REQ-TECH-032); every inserted row has ``user_id = NULL`` and
    ``is_system = TRUE`` (REQ-DB-023).

    Args:
        bind: A Core Connection owned by the caller. This function
            never commits — the caller owns the transaction, which is
            what makes it safe inside an Alembic migration step.

    Returns:
        int: The number of rows inserted (10 on a fresh database, 0 on
            an already-seeded one).
    """
    existing = set(
        bind.execute(
            sa.select(_categories.c.name).where(
                _categories.c.user_id.is_(None)
            )
        )
        .scalars()
        .all()
    )
    rows: list[dict[str, Any]] = [
        {
            "id": uuid.uuid4(),
            "user_id": None,
            "name": entry["name"],
            "color": entry["color"],
            "icon": entry["icon"],
            "is_system": True,
        }
        for entry in SYSTEM_CATEGORIES
        if entry["name"] not in existing
    ]
    if rows:
        bind.execute(sa.insert(_categories), rows)
    return len(rows)

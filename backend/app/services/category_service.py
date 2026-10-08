# mypy: disable-error-code="import-not-found"
"""Category service: list / create / delete + access validator (t11).

Implements Chapter 6 section 6.7 rules on the merged t8 service pattern:
the service owns ``db.commit()`` and the router stays thin. All failures
raise :class:`~app.core.errors.AppError` so the wire shape is always
``{detail, code, field}`` (REQ-ARCH-024).

W3 seam (retired by t13): the expense-count query behind the
delete-in-use 409 lives in :func:`count_expenses_for_category`. Its
body used to import ``app.models.expense`` LAZILY because the model did
not exist before t13; the model has landed, so the import is now a
plain module-level one and the real query always runs. The function
name is contractual (the pinned t11 unit test monkeypatches this exact
module attribute) and t15 re-proves the same path end-to-end. The
file-level ``import-not-found`` pragma above is retained harmlessly
(superseded by t13; ruff/mypy do not object).

Delete 404 taxonomy per Chapter 6 sections 6.7.3/6.7.4 and the groom's
frozen W2 ruling: unknown / cross-user / system deletes are all 404 —
``NOT_FOUND`` for the plain lookup miss (section 6.7.3's reference),
``CATEGORY_NOT_FOUND`` for the system row and for
:func:`validate_category_access` (section 6.7.4's "missing or not
owned" taxonomy). 404 (never 403) so existence is not revealed
(REQ-SEC-032).
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import (
    CATEGORY_IN_USE,
    CATEGORY_NOT_FOUND,
    DUPLICATE_CATEGORY,
    AppError,
)
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User

NOT_FOUND = "NOT_FOUND"
"""Appendix B generic 404 code (field ``-``).

Kept local to this module on purpose: this issue's Definition of Done
pins EXACTLY three new constants in ``app/core/errors.py``
(``DUPLICATE_CATEGORY`` / ``CATEGORY_NOT_FOUND`` / ``CATEGORY_IN_USE``),
and ``NOT_FOUND`` is not one of them — the generic code is Appendix B
verbatim and any later CRUD issue may promote it. The rendered value is
unchanged either way.
"""


def list_categories(session: Session, user: User) -> list[Category]:
    """Return every category the user may see (REQ-BE-060).

    Visibility is ``is_system OR user_id == user.id``; the order is
    ``is_system DESC, name`` so the system block comes first and each
    block is alphabetical (Chapter 6 section 6.7.1). "Alphabetical"
    is case-folded (``func.lower`` tie-break ahead of the raw name) so
    ac1's pinned ``apple`` before ``Zebra`` holds identically on SQLite
    and PostgreSQL, where a raw BINARY ``name`` sort would interleave
    cases. The pinned ordering contract is unchanged for the ten
    capitalized system rows.

    Args:
        session: Active database session.
        user: The caller whose custom categories are included.

    Returns:
        list[Category]: System + the caller's own custom rows only.
    """
    statement = (
        select(Category)
        .where(
            (Category.is_system.is_(True)) | (Category.user_id == user.id),
        )
        .order_by(Category.is_system.desc(), func.lower(Category.name), Category.name)
    )
    return list(session.scalars(statement).all())


def _find_duplicate(session: Session, user: User, name: str) -> Category | None:
    """Find a category whose name collides with ``name`` for ``user``.

    The comparison is case-insensitive (``func.lower``, Chapter 6
    section 6.7.2) and scoped to the caller's own custom names plus the
    system names (REQ-PROD-034); other users' custom names are invisible
    to the check (REQ-DB-022 per-user semantics).

    Args:
        session: Active database session.
        user: The caller.
        name: Already-stripped candidate name.

    Returns:
        Category | None: The colliding row, or ``None``.
    """
    statement = select(Category).where(
        func.lower(Category.name) == name.lower(),
        (Category.user_id == user.id) | (Category.is_system.is_(True)),
    )
    return session.scalars(statement).first()


def create_category(
    session: Session,
    user: User,
    name: str,
    color: str,
    icon: str | None,
) -> Category:
    """Create a custom category owned by ``user`` (REQ-BE-061).

    The name is stripped before the duplicate check and storage
    (Chapter 6 section 6.7.2, builder trap #8).

    Args:
        session: Active database session.
        user: The caller who will own the row.
        name: Candidate name (1-100 chars, validated by the schema).
        color: HEX color (validated by the schema).
        icon: Optional icon identifier.

    Returns:
        Category: The persisted row.

    Raises:
        AppError: 409 DUPLICATE_CATEGORY (field ``name``) when a
            case-insensitive match exists among the caller's own names
            or the system names.
    """
    stripped = name.strip()
    if _find_duplicate(session, user, stripped) is not None:
        raise AppError(409, DUPLICATE_CATEGORY, "Category name already exists", field="name")

    category = Category(user_id=user.id, name=stripped, color=color, icon=icon)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def count_expenses_for_category(session: Session, category_id: uuid.UUID) -> int:
    """Count expense rows referencing ``category_id`` (REQ-BE-062).

    t13 retired the W3 lazy-import seam: ``app.models.expense`` exists
    now, so the import is a plain module-level one and the REAL count
    query always runs (t13 ac5 pins both the 409 with a real expense row
    and the source-level absence of the lazy-import fallback branch).
    The pinned t11 unit test still monkeypatches this exact function
    name, so the seam's test contract is preserved.

    Args:
        session: Active database session.
        category_id: Category primary key to count references for.

    Returns:
        int: Number of expenses using the category.
    """
    count = session.scalar(
        select(func.count()).select_from(Expense).where(Expense.category_id == category_id)
    )
    return int(count or 0)


def delete_category(session: Session, user: User, category_id: uuid.UUID) -> None:
    """Delete the caller's unused custom category (REQ-BE-062).

    Only a non-system row owned by ``user`` is deletable. Every
    not-deletable id is 404 — the FROZEN single status per review_plan
    W2 (the 409 alternative is dead) — with the code split pinned by the
    groom: ``CATEGORY_NOT_FOUND`` for a system row (section 6.7.4's
    taxonomy, Appendix B field ``category_id``) and ``NOT_FOUND`` for an
    unknown or cross-user id (section 6.7.3's reference, field ``None``).

    Args:
        session: Active database session.
        user: The caller.
        category_id: Path-parameter category uuid.

    Raises:
        AppError: 404 CATEGORY_NOT_FOUND for system ids, 404 NOT_FOUND
            for unknown / cross-user ids, or 409 CATEGORY_IN_USE (field
            ``category_id``) while expenses reference the category.
    """
    category = session.scalars(select(Category).where(Category.id == category_id)).first()
    if category is None:
        raise AppError(404, NOT_FOUND, "Category not found")
    if category.is_system:
        raise AppError(
            404, CATEGORY_NOT_FOUND, "Category not found", field="category_id"
        )
    if category.user_id != user.id:
        raise AppError(404, NOT_FOUND, "Category not found")

    if count_expenses_for_category(session, category_id) > 0:
        raise AppError(409, CATEGORY_IN_USE, "Category is used by expenses", field="category_id")

    session.delete(category)
    session.commit()


def validate_category_access(session: Session, user: User, category_id: uuid.UUID) -> Category:
    """Return the category ``user`` may write expenses against (REQ-BE-063).

    A category is usable iff ``is_system OR user_id == user.id``. The
    failure is 404 ``CATEGORY_NOT_FOUND`` (never 403) so a cross-user id
    does not reveal existence (REQ-SEC-032). This is the contract t13's
    expense writes consume.

    Args:
        session: Active database session.
        user: The caller.
        category_id: Category primary key to validate.

    Returns:
        Category: The usable row.

    Raises:
        AppError: 404 CATEGORY_NOT_FOUND (field ``category_id``) for
            unknown ids and other users' custom categories.
    """
    statement = select(Category).where(
        Category.id == category_id,
        (Category.is_system.is_(True)) | (Category.user_id == user.id),
    )
    category = session.scalars(statement).first()
    if category is None:
        raise AppError(404, CATEGORY_NOT_FOUND, "Category not found", field="category_id")
    return category


__all__ = [
    "count_expenses_for_category",
    "create_category",
    "delete_category",
    "list_categories",
    "validate_category_access",
]

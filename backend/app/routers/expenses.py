"""Expense endpoints: list/create/get/update/delete (t13, REQ-API-040..044).

The router is mounted under ``/api/v1/expenses`` and registered in
``create_app()`` AFTER the health, auth and categories routers (the
merged registration-order precedent, pinned by the OpenAPI node). It
follows the merged t8/t11 pattern: ``Annotated[T, Depends(...)]`` DI
(ruff B008), thin bodies that delegate to
:mod:`app.services.expense_service`, and every error rendered
``{detail, code, field}`` through the ``AppError`` handler.

Contract pins:

* The list response is the frozen W6 envelope
  ``{items, total, page, page_size}``; an out-of-range but well-formed
  ``page`` is 200 with empty items (Chapter 7 7.5.1 lists only
  200/422), and the query bounds ``page >= 1``, ``1 <= page_size <= 100``
  and the ``year_month`` pattern render 422 VALIDATION_ERROR through the
  merged ``RequestValidationError`` handler.
* ``PUT`` bodies must carry at least one field (Chapter 7 7.5.4
  ``minProperties: 1``): the ``extra="forbid"`` schema plus the
  ``model_fields_set`` guard below reject ``{}`` with 422
  VALIDATION_ERROR without touching the row.
* No route here can answer 403: ownership misses are 404 in the
  service (REQ-SEC-031).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_client_ip, get_current_user
from app.core.errors import VALIDATION_ERROR, AppError
from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import (
    CreateExpenseRequest,
    ExpenseListResponse,
    ExpenseResponse,
    UpdateExpenseRequest,
)
from app.services import expense_service

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

YEAR_MONTH_PATTERN = r"^[0-9]{4}-[0-9]{2}$"
"""year_month query filter format (Chapter 7 7.5.1)."""


def _to_response(expense: Expense) -> ExpenseResponse:
    """Build the frozen ten-key response from an ORM row.

    Args:
        expense: The row with its ``category`` relationship loaded.

    Returns:
        ExpenseResponse: The public representation.
    """
    return ExpenseResponse(
        id=expense.id,
        amount=expense.amount,
        currency=expense.currency,
        category_id=expense.category_id,
        category_name=expense.category.name,
        category_color=expense.category.color,
        date=expense.date,
        note=expense.note,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


@router.get("", response_model=ExpenseListResponse)
def list_expenses(
    session: SessionDep,
    current_user: CurrentUser,
    year_month: Annotated[str | None, Query(pattern=YEAR_MONTH_PATTERN)] = None,
    category_id: Annotated[uuid.UUID | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ExpenseListResponse:
    """List the caller's expenses with filters and pagination (REQ-API-040).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller (queries are scoped to them).
        year_month: Optional ``YYYY-MM`` month filter.
        category_id: Optional category filter.
        page: 1-based page number (out-of-range pages return no items).
        page_size: Rows per page, 1-100.

    Returns:
        ExpenseListResponse: The frozen four-key W6 envelope.
    """
    items, total = expense_service.list_expenses(
        session,
        current_user,
        year_month=year_month,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )
    return ExpenseListResponse(
        items=[_to_response(row) for row in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    body: CreateExpenseRequest,
    session: SessionDep,
    current_user: CurrentUser,
    client_ip: Annotated[str | None, Depends(get_client_ip)],
) -> ExpenseResponse:
    """Create an expense for the caller (REQ-API-041).

    Args:
        body: Validated create payload.
        session: Request-scoped database session.
        current_user: Authenticated caller who owns the new row.
        client_ip: Best-effort client IP for the audit row.

    Returns:
        ExpenseResponse: The persisted row in the ten-key shape.

    Raises:
        AppError: 422 INVALID_AMOUNT or 404 CATEGORY_NOT_FOUND.
    """
    expense = expense_service.create_expense(
        session,
        current_user,
        amount=body.amount,
        category_id=body.category_id,
        date=body.date,
        note=body.note,
        ip_address=client_ip,
    )
    return _to_response(expense)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> ExpenseResponse:
    """Return one of the caller's expenses (REQ-API-042).

    Args:
        expense_id: Expense uuid (Appendix B field pin).
        session: Request-scoped database session.
        current_user: Authenticated caller.

    Returns:
        ExpenseResponse: The row in the ten-key shape.

    Raises:
        AppError: 404 NOT_FOUND for unknown / cross-user ids.
    """
    expense = expense_service.get_expense(session, current_user, expense_id)
    return _to_response(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: uuid.UUID,
    body: UpdateExpenseRequest,
    session: SessionDep,
    current_user: CurrentUser,
    client_ip: Annotated[str | None, Depends(get_client_ip)],
) -> ExpenseResponse:
    """Partially update one of the caller's expenses (REQ-API-043).

    Args:
        expense_id: Expense uuid.
        body: Partial update payload (>= 1 field, minProperties pin).
        session: Request-scoped database session.
        current_user: Authenticated caller.
        client_ip: Best-effort client IP for the audit row.

    Returns:
        ExpenseResponse: The updated row.

    Raises:
        AppError: 422 VALIDATION_ERROR (empty body), 404 NOT_FOUND, 404
            CATEGORY_NOT_FOUND, or 422 INVALID_AMOUNT.
    """
    if not body.model_fields_set:
        raise AppError(
            422,
            VALIDATION_ERROR,
            "At least one field is required",
            field=None,
        )
    expense = expense_service.update_expense(
        session,
        current_user,
        expense_id,
        amount=body.amount,
        category_id=body.category_id,
        date=body.date,
        note=body.note,
        note_sent="note" in body.model_fields_set,
        ip_address=client_ip,
    )
    return _to_response(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_expense(
    expense_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    client_ip: Annotated[str | None, Depends(get_client_ip)],
) -> None:
    """Delete one of the caller's expenses (REQ-API-044).

    Args:
        expense_id: Expense uuid.
        session: Request-scoped database session.
        current_user: Authenticated caller.
        client_ip: Best-effort client IP for the audit row.

    Returns:
        None: 204 with an empty body.

    Raises:
        AppError: 404 NOT_FOUND for unknown / cross-user ids.
    """
    expense_service.delete_expense(session, current_user, expense_id, ip_address=client_ip)
    return None

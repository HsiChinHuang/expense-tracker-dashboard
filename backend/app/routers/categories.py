"""Category endpoints: list / create / delete (t11, REQ-API-030/031/032).

The router is mounted under ``/api/v1/categories`` and registered in
``create_app()`` AFTER the health and auth routers (t8's registration-
order precedent, pinned by ac5's openapi node). It follows the merged
t8 pattern: ``Annotated[T, Depends(...)]`` DI (ruff B008), thin bodies
that delegate to :mod:`app.services.category_service`, and every error
rendered ``{detail, code, field}`` through the ``AppError`` handler.

There is deliberately NO update route: Chapter 7 section 7.4.3 defines
only GET/POST/DELETE and system-category immutability is pinned as an
OpenAPI absence check (review_plan W2, REQ-PROD-034).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryListResponse,
    CategoryResponse,
    CreateCategoryRequest,
)
from app.services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=CategoryListResponse)
def list_categories(
    session: SessionDep,
    current_user: CurrentUser,
) -> CategoryListResponse:
    """List the caller's visible categories (FR-CAT-1, REQ-API-030).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller.

    Returns:
        CategoryListResponse: ``{"categories": [...]}`` with the ten
        system rows first, then the caller's custom rows, alphabetical
        inside each block.
    """
    rows = category_service.list_categories(session, current_user)
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(row) for row in rows]
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CreateCategoryRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> Category:
    """Create a custom category for the caller (FR-CAT-2, REQ-API-031).

    Args:
        body: Validated create payload (name/color/icon bounds owned by
            the Pydantic schema per review_plan W4).
        session: Request-scoped database session.
        current_user: Authenticated caller who owns the new row.

    Returns:
        Category: The persisted row (six public fields only).

    Raises:
        AppError: 409 DUPLICATE_CATEGORY (field ``name``).
    """
    return category_service.create_category(
        session, current_user, body.name, body.color, body.icon
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_category(
    category_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Delete the caller's unused custom category (REQ-API-032).

    Args:
        category_id: Category uuid (Appendix B field pin).
        session: Request-scoped database session.
        current_user: Authenticated caller.

    Returns:
        None: 204 with an empty body.

    Raises:
        AppError: 404 NOT_FOUND / CATEGORY_NOT_FOUND (unknown, cross-user,
            or system id — single frozen 404 per review_plan W2), or 409
            CATEGORY_IN_USE (field ``category_id``).
    """
    category_service.delete_category(session, current_user, category_id)
    return None

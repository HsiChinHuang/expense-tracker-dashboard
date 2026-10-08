"""Pydantic request/response schemas for the category endpoints (t11).

Chapter 7 section 7.4.2 is the contract source: the create body is
``{name (1-100 chars), color (HEX pattern), icon? (<=50 chars)}`` and the
public category representation is exactly the six keys
``{id, name, color, icon, is_system, created_at}`` — ``user_id`` is never
exposed (REQ-API-030/031). The GET 200 body is the OBJECT WRAPPER
``{"categories": [...]}``, not a bare array (section 7.4.1; t16 mirrors
this shape).

review_plan W4 ruling: the name length bound is enforced HERE (Field
min_length/max_length verbatim from the chapter), not by a DB CHECK —
REQ-DB-021 defines only the HEX and system-consistency CHECKs and SQLite
would not enforce VARCHAR(100) anyway. The color pattern mirrors the
merged ``ck_categories_color_format`` CHECK semantics in the regex form
the chapter pins.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"
"""Canonical 6-digit HEX color (Chapter 7 section 7.4.2 verbatim)."""

NAME_MIN_LENGTH = 1
"""Minimum category name length (Chapter 7 section 7.4.2)."""

NAME_MAX_LENGTH = 100
"""Maximum category name length (Chapter 7 section 7.4.2, W4 pin)."""

ICON_MAX_LENGTH = 50
"""Maximum icon identifier length (Chapter 7 section 7.4.2)."""


class CreateCategoryRequest(BaseModel):
    """Request body for ``POST /api/v1/categories`` (REQ-API-031).

    Attributes:
        name: Category name, 1-100 characters (W4: Pydantic-owned bound).
        color: HEX color such as ``#EF4444`` (case-insensitive hex digits).
        icon: Optional icon identifier, at most 50 characters.
    """

    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    color: str = Field(pattern=HEX_COLOR_PATTERN)
    icon: str | None = Field(default=None, max_length=ICON_MAX_LENGTH)


class CategoryResponse(BaseModel):
    """Public category representation — exactly six fields (REQ-API-030).

    ``from_attributes`` lets routes build it from the ORM ``Category``
    row; the model deliberately has no ``user_id`` field so ownership can
    never leak through the API.

    Attributes:
        id: Category UUID (serialized as its canonical string form).
        name: Stored category name.
        color: Stored HEX color.
        icon: Icon identifier, or ``None``.
        is_system: True for the ten seeded system categories.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color: str
    icon: str | None
    is_system: bool
    created_at: datetime


class CategoryListResponse(BaseModel):
    """Response body for ``GET /api/v1/categories`` (REQ-API-030).

    The object wrapper is contractual (Chapter 7 section 7.4.1); a bare
    array would break t16's mirrored client type.

    Attributes:
        categories: Visible categories, system block first then the
            caller's custom ones, alphabetical inside each block.
    """

    categories: list[CategoryResponse]

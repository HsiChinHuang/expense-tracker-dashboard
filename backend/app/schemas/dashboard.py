"""Pydantic response schemas for the six dashboard endpoints (t19).

Chapter 7 sections 7.7.1..7.7.6 define the wire shapes; the FROZEN
issue contract (docs/issues/t19.md, pinned decisions 1/5/7/10) is the
authoritative key set and wins over the chapter pseudocode where the
two name keys differently:

* Summary: exactly ``{year_month, total, budget_amount, remaining,
  percentage, is_over_budget, category_count}`` — money fields are
  2-dp STRINGS (plan ruling 6) and ``percentage`` is a JSON NUMBER or
  ``null`` (null exactly when the budget is 0), never a string
  (groom ruling 1/9).
* By-category: top level ``{year_month, total, categories}`` with rows
  carrying exactly the five keys ``{category_id, category_name, color,
  amount, percentage}`` (issue ac3).
* Trend items are ``{year_month, total}`` — no label field (groom
  ruling 5).
* Cumulative day objects are the SERVICE keys ``{date, daily,
  cumulative}`` (issue contract correction, NOT ``daily_total``).
* Heatmap weeks are ``{week_start, days}`` with seven ``{date,
  amount}`` days each.
* Recent reuses the merged ten-key ``ExpenseResponse`` shape verbatim
  (groom ruling 7) — this module deliberately RE-EXPORTS it so t20+
  has one dashboard module to import from.

The service returns fully-formatted plain dicts (Chapter 6 shapes);
these models are declared ``from_attributes``-free thin envelopes with
``extra="allow"`` so the FROZEN observable key set is whatever the
service emits — the integration tests pin the keys, and response_model
is optional per groom ruling 10.
"""

from pydantic import BaseModel

from app.schemas.expense import ExpenseResponse

__all__ = [
    "DashboardByCategoryResponse",
    "DashboardCumulativeResponse",
    "DashboardHeatmapResponse",
    "DashboardRecentResponse",
    "DashboardSummaryResponse",
    "DashboardTrendResponse",
    "ExpenseResponse",
]


class _Envelope(BaseModel):
    """Base for the dashboard envelopes (service dict passes through).

    The service layer owns the frozen key sets and the 2-dp string
    formatting; these models exist for OpenAPI documentation only and
    therefore accept any payload the service produces.
    """

    model_config = {"extra": "allow"}


class DashboardSummaryResponse(_Envelope):
    """``GET /api/v1/dashboard/summary`` body (Chapter 7 7.7.1)."""


class DashboardByCategoryResponse(_Envelope):
    """``GET /api/v1/dashboard/by-category`` body (Chapter 7 7.7.2)."""


class DashboardTrendResponse(_Envelope):
    """``GET /api/v1/dashboard/trend`` body (Chapter 7 7.7.3)."""


class DashboardCumulativeResponse(_Envelope):
    """``GET /api/v1/dashboard/cumulative`` body (Chapter 7 7.7.4)."""


class DashboardHeatmapResponse(_Envelope):
    """``GET /api/v1/dashboard/heatmap`` body (Chapter 7 7.7.5)."""


class DashboardRecentResponse(BaseModel):
    """``GET /api/v1/dashboard/recent`` body (Chapter 7 7.7.6).

    Attributes:
        items: Recent expenses in the merged ten-key expense shape
            (groom ruling 7 — the very same ``ExpenseResponse`` the
            expenses router serves).
    """

    items: list[ExpenseResponse]

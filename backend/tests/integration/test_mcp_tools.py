# mypy: disable-error-code="import-untyped"
"""Integration tests for the four MCP tool modules (REQ-PLAN-061, REQ-AI-082..093).

The whole vertical is executed ENTIRELY in-process: an ``httpx.MockTransport``
stands in for the backend, so every request the tools build is recorded
without any network egress, and the transport's call count is the evidence
that rejection paths never reach the wire. Tokens are minted by the merged
backend primitive ``create_access_token`` and verified by the MCP-side
``verify_jwt`` against the same secret pinned through the environment (the
t7 precedent), so acceptance and rejection exercise the real JWT rules.

The 12 collected node IDs are a frozen contract: four happy paths (bearer
header, simplified budget shape, by-category rows, the ``limit`` ->
``page_size`` mapping plus the ``category`` -> ``category_id`` filter), four
rejection-before-dispatch paths (invalid signature, expired, wrong audience,
wrong ``type`` claim -- each with the call count frozen at zero), the non-2xx
raise, and the two amount-guardrail rejections that must also leave the call
count at zero.

The MCP modules live outside the backend project under ``mcp-server/`` and
import their siblings by bare name (``auth``, ``config``, ``tools``), so the
helper below extends ``sys.path`` and imports them lazily by module name.
"""

import importlib
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from jose import jwt as jose_jwt

from app.auth.jwt import create_access_token
from app.config import get_settings

MCP_DIR = Path(__file__).resolve().parents[3] / "mcp-server"

TEST_SECRET = "integration-test-mcp-secret-not-a-real-key"
WRONG_SECRET = "integration-test-other-secret-not-a-real-key"
TEST_ISSUER = "expense-tracker"
TEST_AUDIENCE = "expense-tracker-api"
SUBJECT = "user-42"
BASE_URL = "http://backend.invalid/api/v1"


def _mcp(module_name: str) -> Any:
    """Import one mcp-server module by bare name.

    Args:
        module_name: Bare module name such as ``auth`` or ``tools.add_expense``.

    Returns:
        Any: The imported module (dynamically located imports cannot be
        statically typed).
    """
    if str(MCP_DIR) not in sys.path:
        sys.path.insert(0, str(MCP_DIR))
    return importlib.import_module(module_name)


def _forged_token(**overrides: Any) -> str:
    """Mint a token with the pinned secret and claim overrides.

    Args:
        overrides: Claims replacing the defaults (e.g. ``exp``, ``aud``).

    Returns:
        str: A compact JWS the MCP verifier must reject.
    """
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": SUBJECT,
        "iss": TEST_ISSUER,
        "aud": TEST_AUDIENCE,
        "iat": now,
        "exp": now + 3600,
        "type": "access",
    }
    claims.update(overrides)
    return cast(str, jose_jwt.encode(claims, TEST_SECRET, algorithm="HS256"))


class Recorder:
    """Records every request the transport receives and answers it."""

    def __init__(self, status_code: int = 200, body: Any = None) -> None:
        """Store the canned answer; the request list starts empty."""
        self.status_code = status_code
        self.body: Any = body if body is not None else {}
        self.requests: list[httpx.Request] = []

    @property
    def calls(self) -> int:
        """Return how many requests reached the transport."""
        return len(self.requests)

    def transport(self) -> httpx.BaseTransport:
        """Return a MockTransport that records requests and answers canned."""
        return httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        """Record *request* and answer with the canned status/body."""
        self.requests.append(request)
        return httpx.Response(self.status_code, json=self.body)


@pytest.fixture(autouse=True)
def _pin_mcp_jwt(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin backend JWT settings and mirror them into the MCP auth module.

    The backend primitive signs with ``settings.JWT_SECRET`` and the MCP
    verifier reads ``auth.MCP_JWT_SECRET``; both are pointed at the same
    test secret, and a valid access token is installed as the user token so
    happy paths dispatch. The settings cache is cleared on teardown so the
    pinned values cannot leak into later tests in the same process.

    Args:
        monkeypatch: pytest monkeypatch for environment and attribute pinning.

    Yields:
        None: Control returns with the pinned identity active.
    """
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    monkeypatch.setenv("JWT_ISSUER", TEST_ISSUER)
    monkeypatch.setenv("JWT_AUDIENCE", TEST_AUDIENCE)
    get_settings.cache_clear()

    auth = _mcp("auth")
    monkeypatch.setattr(auth, "MCP_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(auth, "MCP_USER_TOKEN", create_access_token(SUBJECT))
    yield
    get_settings.cache_clear()


def test_valid_token_reaches_transport_with_bearer_header() -> None:
    """A valid MCP token is sent as the Bearer header on the frozen call."""
    recorder = Recorder(body={"items": [], "total": 0, "page": 1, "page_size": 5})
    result = _mcp("tools.list_expenses").run(
        {"page": 1, "limit": 5}, ("GET", "/expenses"), BASE_URL, recorder.transport()
    )

    assert recorder.calls == 1
    request = recorder.requests[0]
    assert request.method == "GET"
    assert request.url.path == "/api/v1/expenses"
    token = _mcp("auth").MCP_USER_TOKEN
    assert request.headers["authorization"] == f"Bearer {token}"
    assert result["page_size"] == 5


def test_get_budget_status_calls_summary_and_simplifies() -> None:
    """The summary endpoint is called once and the answer is simplified."""
    upstream = {
        "year_month": "2026-03",
        "total": "120.50",
        "budget_amount": "500.00",
        "remaining": "379.50",
        "percentage": 24.1,
        "is_over_budget": False,
        "category_count": 3,
    }
    recorder = Recorder(body=upstream)
    result = _mcp("tools.get_budget_status").run(
        {"year_month": "2026-03"}, ("GET", "/dashboard/summary"), BASE_URL, recorder.transport()
    )

    assert recorder.calls == 1
    request = recorder.requests[0]
    assert request.url.path == "/api/v1/dashboard/summary"
    assert request.url.params["year_month"] == "2026-03"
    assert result == {
        "total_spent": "120.50",
        "total_budget": "500.00",
        "remaining": "379.50",
        "percentage": 24.1,
    }


def test_monthly_summary_returns_by_category_rows() -> None:
    """The by-category endpoint is called once and its rows are returned."""
    rows = [
        {
            "category_id": "c1",
            "category_name": "Food",
            "color": "#fff",
            "amount": "80.00",
            "percentage": 66.4,
        },
        {
            "category_id": "c2",
            "category_name": "Fun",
            "color": "#000",
            "amount": "40.50",
            "percentage": 33.6,
        },
    ]
    recorder = Recorder(body={"year_month": "2026-03", "total": "120.50", "categories": rows})
    result = _mcp("tools.monthly_summary").run(
        {"year_month": "2026-03"},
        ("GET", "/dashboard/by-category"),
        BASE_URL,
        recorder.transport(),
    )

    assert recorder.calls == 1
    request = recorder.requests[0]
    assert request.url.path == "/api/v1/dashboard/by-category"
    assert result["categories"] == rows
    assert result["total"] == "120.50"


def test_list_expenses_limit_maps_to_page_size() -> None:
    """The tool-facing ``limit`` parameter becomes the API ``page_size``."""
    recorder = Recorder(body={"items": [], "total": 0, "page": 1, "page_size": 5})
    _mcp("tools.list_expenses").run(
        {"limit": 5}, ("GET", "/expenses"), BASE_URL, recorder.transport()
    )

    assert recorder.calls == 1
    params = recorder.requests[0].url.params
    assert params["page_size"] == "5"
    assert "limit" not in params


def test_list_expenses_category_filter_maps_to_category_id() -> None:
    """The tool-facing ``category`` filter becomes the API ``category_id``."""
    recorder = Recorder(body={"items": [], "total": 0, "page": 1, "page_size": 20})
    _mcp("tools.list_expenses").run(
        {"category": "11111111-1111-1111-1111-111111111111", "month": "2026-03"},
        ("GET", "/expenses"),
        BASE_URL,
        recorder.transport(),
    )

    assert recorder.calls == 1
    params = recorder.requests[0].url.params
    assert params["category_id"] == "11111111-1111-1111-1111-111111111111"
    assert params["year_month"] == "2026-03"
    assert "category" not in params
    assert "month" not in params


def test_invalid_signature_is_rejected_before_any_transport_call() -> None:
    """A token signed with another secret never reaches the transport."""
    auth = _mcp("auth")
    forged = cast(
        str,
        jose_jwt.encode(
            {
                "sub": SUBJECT,
                "iss": TEST_ISSUER,
                "aud": TEST_AUDIENCE,
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600,
                "type": "access",
            },
            WRONG_SECRET,
            algorithm="HS256",
        ),
    )
    auth.MCP_USER_TOKEN = forged
    recorder = Recorder()

    with pytest.raises(auth.AuthError):
        auth.verify_jwt(auth.get_user_token())
    with pytest.raises(auth.AuthError):
        _mcp("tools.list_expenses").run(
            {}, ("GET", "/expenses"), BASE_URL, recorder.transport()
        )
    assert recorder.calls == 0


def test_expired_token_is_rejected_before_any_transport_call() -> None:
    """An expired token is refused by verify_jwt with zero transport calls."""
    auth = _mcp("auth")
    auth.MCP_USER_TOKEN = _forged_token(exp=int(time.time()) - 60)
    recorder = Recorder()

    with pytest.raises(auth.AuthError):
        _mcp("tools.get_budget_status").run(
            {"year_month": "2026-03"},
            ("GET", "/dashboard/summary"),
            BASE_URL,
            recorder.transport(),
        )
    assert recorder.calls == 0


def test_wrong_audience_is_rejected_before_any_transport_call() -> None:
    """A token minted for another audience is refused before dispatch."""
    auth = _mcp("auth")
    auth.MCP_USER_TOKEN = _forged_token(aud="someone-else")
    recorder = Recorder()

    with pytest.raises(auth.AuthError):
        _mcp("tools.monthly_summary").run(
            {"year_month": "2026-03"},
            ("GET", "/dashboard/by-category"),
            BASE_URL,
            recorder.transport(),
        )
    assert recorder.calls == 0


def test_wrong_type_claim_is_rejected_before_any_transport_call() -> None:
    """A refresh-typed token is refused: only access tokens dispatch."""
    auth = _mcp("auth")
    auth.MCP_USER_TOKEN = _forged_token(type="refresh")
    recorder = Recorder()

    with pytest.raises(auth.AuthError):
        _mcp("tools.list_expenses").run(
            {}, ("GET", "/expenses"), BASE_URL, recorder.transport()
        )
    assert recorder.calls == 0


def test_non_2xx_response_raises_mcp_tool_error() -> None:
    """A 500 answer becomes McpToolError, not a bare exception path."""
    recorder = Recorder(status_code=500, body={"detail": "boom"})
    mcp_tools = _mcp("tools")

    with pytest.raises(mcp_tools.McpToolError):
        _mcp("tools.list_expenses").run(
            {"limit": 5}, ("GET", "/expenses"), BASE_URL, recorder.transport()
        )
    assert recorder.calls == 1


def test_over_max_amount_raises_value_error_with_zero_requests() -> None:
    """The t30 guardrail rejects an over-ceiling amount before any request."""
    recorder = Recorder(status_code=201, body={})

    with pytest.raises(ValueError):
        _mcp("tools.add_expense").run(
            {"amount": "1000000000.00", "category_id": "c1", "date": "2026-03-01"},
            ("POST", "/expenses"),
            BASE_URL,
            recorder.transport(),
        )
    assert recorder.calls == 0


def test_three_decimal_amount_raises_value_error_with_zero_requests() -> None:
    """The t30 guardrail rejects a 3-decimal amount before any request."""
    recorder = Recorder(status_code=201, body={})

    with pytest.raises(ValueError):
        _mcp("tools.add_expense").run(
            {"amount": "12.345", "category_id": "c1", "date": "2026-03-01"},
            ("POST", "/expenses"),
            BASE_URL,
            recorder.transport(),
        )
    assert recorder.calls == 0

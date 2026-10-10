"""``monthly_summary``: one GET on the by-category endpoint (REQ-EXT-036).

The tool returns the by-category rows for one month -- the upstream
``categories`` list plus the month and its grand total -- so the agent can
read a breakdown without learning the backend's response envelope. The call is
the module's single frozen request and any non-2xx answer becomes
:class:`McpToolError` (REQ-AI-084, REQ-AI-087).
"""

from typing import Any

import httpx
from auth import get_user_token, verify_jwt
from config import MCP_API_BASE_URL
from tools import McpToolError

FROZEN_PATH = "/dashboard/by-category"
"""The only endpoint this tool may call (t31 ac5's frozen map)."""


def run(
    arguments: dict[str, Any],
    endpoint: tuple[str, str] | None = None,
    base_url: str | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    """Return the per-category breakdown for one month.

    Args:
        arguments: Tool arguments carrying ``year_month`` (``YYYY-MM``).
        endpoint: The frozen ``(method, path)`` pair the server dispatches
            with; only ``("GET", "/dashboard/by-category")`` is ever issued.
        base_url: API base URL, defaulting to the configured one.
        transport: Optional httpx transport so tests can stand in for the
            backend without any network egress.

    Returns:
        dict[str, Any]: ``year_month``, ``total`` and the ``categories`` rows.

    Raises:
        AuthError: The bearer token is missing or is not a valid access token.
        ValueError: The dispatch endpoint is not this tool's frozen pair.
        McpToolError: The API answered with a non-2xx status.
    """
    verify_jwt(get_user_token())

    if endpoint is not None and endpoint != ("GET", FROZEN_PATH):
        raise ValueError(f"monthly_summary may only call GET {FROZEN_PATH}")

    params: dict[str, Any] = {"year_month": arguments["year_month"]}
    headers = {"Authorization": f"Bearer {get_user_token()}"}
    url = f"{base_url or MCP_API_BASE_URL}{FROZEN_PATH}"

    with httpx.Client(transport=transport) as client:
        response = client.get(url, params=params, headers=headers)

    if not 200 <= response.status_code < 300:
        raise McpToolError(f"GET {FROZEN_PATH} failed with status {response.status_code}")

    body: dict[str, Any] = response.json()
    return {
        "year_month": body["year_month"],
        "total": body["total"],
        "categories": body["categories"],
    }

"""``list_expenses``: one GET on the expense list with the tool-side filters (REQ-EXT-037).

The tool contract differs from the API contract in three places, and this
module owns the translation: ``limit`` becomes the API's ``page_size``,
``category`` becomes ``category_id`` and ``month`` becomes ``year_month``.
The query string therefore carries the API's literal key names while the
agent-facing parameters keep the tool's names. The call is the module's single
frozen request and any non-2xx answer becomes :class:`McpToolError`
(REQ-AI-084, REQ-AI-087).
"""

from typing import Any

import httpx
from auth import get_user_token, verify_jwt
from config import MCP_API_BASE_URL
from tools import McpToolError

FROZEN_PATH = "/expenses"
"""The only endpoint this tool may call (t31 ac5's frozen map)."""


def run(
    arguments: dict[str, Any],
    endpoint: tuple[str, str] | None = None,
    base_url: str | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    """List the caller's expenses through the API's pagination contract.

    Args:
        arguments: Tool arguments. ``page`` and ``limit`` are optional; the
            optional ``category`` and ``month`` filters map onto the API's
            ``category_id`` and ``year_month`` queries.
        endpoint: The frozen ``(method, path)`` pair the server dispatches
            with; only ``("GET", "/expenses")`` is ever issued.
        base_url: API base URL, defaulting to the configured one.
        transport: Optional httpx transport so tests can stand in for the
            backend without any network egress.

    Returns:
        dict[str, Any]: The API's ``{items, total, page, page_size}`` envelope.

    Raises:
        AuthError: The bearer token is missing or is not a valid access token.
        ValueError: The dispatch endpoint is not this tool's frozen pair.
        McpToolError: The API answered with a non-2xx status.
    """
    verify_jwt(get_user_token())

    if endpoint is not None and endpoint != ("GET", FROZEN_PATH):
        raise ValueError(f"list_expenses may only call GET {FROZEN_PATH}")

    limit = arguments["limit"] if "limit" in arguments else None
    page = arguments["page"] if "page" in arguments else None
    category = arguments["category"] if "category" in arguments else None
    month = arguments["month"] if "month" in arguments else None

    params: dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["page_size"] = limit
    if category is not None:
        params["category_id"] = category
    if month is not None:
        params["year_month"] = month

    headers = {"Authorization": f"Bearer {get_user_token()}"}
    url = f"{base_url or MCP_API_BASE_URL}{FROZEN_PATH}"

    with httpx.Client(transport=transport) as client:
        response = client.get(url, params=params, headers=headers)

    if not 200 <= response.status_code < 300:
        raise McpToolError(f"GET {FROZEN_PATH} failed with status {response.status_code}")

    result: dict[str, Any] = response.json()
    return result

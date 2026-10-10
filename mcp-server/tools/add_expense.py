"""``add_expense``: validate the amount, then POST one expense (REQ-EXT-034).

The guardrail comes first: the t30 ``validate-amount.py`` hook is loaded by
path and applied BEFORE the payload is built and BEFORE any request leaves the
process, so a rejected amount never reaches the API (REQ-AI-093). The hook is
loaded dynamically because its file name is hyphenated and therefore not an
import identifier (the same loader contract t30's own tests use).

The request is the single frozen call of this module -- ``POST /expenses`` --
carrying the caller's bearer token, and any non-2xx answer becomes
:class:`McpToolError` (REQ-AI-084, REQ-AI-087).
"""

import importlib.util
from pathlib import Path
from typing import Any

import httpx
from auth import get_user_token, verify_jwt
from config import MCP_API_BASE_URL
from tools import McpToolError

FROZEN_PATH = "/expenses"
"""The only endpoint this tool may call (t31 ac5's frozen map)."""

HOOK_PATH = Path(__file__).resolve().parents[2] / "agent-hooks" / "validate-amount.py"
"""Repository location of the t30 amount guardrail hook."""


def load_validator() -> Any:
    """Load and return the t30 ``validate_amount`` callable.

    Returns:
        Any: The hook's ``validate_amount`` function (a dynamically loaded
        module cannot be statically typed).

    Raises:
        McpToolError: The hook file or its loader is unavailable, so the
            guardrail cannot be applied and no request may be issued.
    """
    if not HOOK_PATH.is_file():
        raise McpToolError(f"amount guardrail hook not found: {HOOK_PATH}")

    spec = importlib.util.spec_from_file_location("agent_hook_validate_amount", HOOK_PATH)
    if spec is None or spec.loader is None:
        raise McpToolError(f"amount guardrail hook has no loader: {HOOK_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_amount


def run(
    arguments: dict[str, Any],
    endpoint: tuple[str, str] | None = None,
    base_url: str | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    """Validate the amount and record one expense through the public API.

    Args:
        arguments: Tool arguments carrying ``amount``, ``category_id``,
            ``date`` and the optional ``note``.
        endpoint: The frozen ``(method, path)`` pair the server dispatches
            with; only ``("POST", "/expenses")`` is ever issued.
        base_url: API base URL, defaulting to the configured one.
        transport: Optional httpx transport so tests can stand in for the
            backend without any network egress.

    Returns:
        dict[str, Any]: The created expense as returned by the API.

    Raises:
        AuthError: The bearer token is missing or is not a valid access token.
        ValueError: The amount violates the t30 guardrail rules, or a required
            argument is missing.
        McpToolError: The API answered with a non-2xx status.
    """
    verify_jwt(get_user_token())

    if endpoint is not None and endpoint != ("POST", FROZEN_PATH):
        raise ValueError(f"add_expense may only call POST {FROZEN_PATH}")

    validate_amount = load_validator()
    amount = validate_amount(arguments["amount"])

    payload: dict[str, Any] = {
        "amount": f"{amount:.2f}",
        "category_id": arguments["category_id"],
        "date": arguments["date"],
    }
    if "note" in arguments and arguments["note"] is not None:
        payload["note"] = arguments["note"]

    headers = {"Authorization": f"Bearer {get_user_token()}"}
    url = f"{base_url or MCP_API_BASE_URL}{FROZEN_PATH}"

    with httpx.Client(transport=transport) as client:
        response = client.post(url, json=payload, headers=headers)

    if not 200 <= response.status_code < 300:
        raise McpToolError(f"POST {FROZEN_PATH} failed with status {response.status_code}")

    result: dict[str, Any] = response.json()
    return result

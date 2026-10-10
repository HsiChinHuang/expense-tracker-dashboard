"""MCP server core: a transport-agnostic newline-delimited JSON-RPC 2.0 loop.

The server speaks the MCP wire protocol directly over stdio (no SDK, no
network listener): one JSON object per line read from ``sys.stdin``, one JSON
object per line written to ``stdout``. The three handled methods are
``initialize``, ``tools/list`` and ``tools/call``; anything else answers with a
JSON-RPC ``error`` object (REQ-AI-082, REQ-AI-085, REQ-EXT-031, REQ-EXT-081).

``list_tools`` returns EXACTLY the four frozen tool definitions with strict
JSON-schema inputs (typed properties, required lists, no extra keys), and
``call_tool`` verifies the caller's JWT BEFORE any dispatch and then routes to
the matching ``tools/<name>.py`` module. The tool modules perform the actual
API request with httpx against the frozen endpoint map below -- the server
never touches a database and never adds a backend route (REQ-AI-080/087,
REQ-EXT-030, REQ-ARCH-002).

The four operation names and the four API paths are FROZEN by this card's ac5;
a fifth tool or an unrelated path breaks REQ-AI-085/REQ-PROD-043 and the t29
skills surface.
"""

import importlib
import json
import sys
from typing import Any, cast

from auth import AuthError, get_user_token, verify_jwt
from config import MCP_API_BASE_URL

PROTOCOL_VERSION: str = "2024-11-05"
"""MCP protocol revision advertised by the initialize response."""

SERVER_NAME: str = "expense-tracker-mcp"
"""Server identity reported during initialization."""

SERVER_VERSION: str = "0.1.0"
"""Server version reported during initialization."""

PARSE_ERROR: int = -32700
INVALID_REQUEST: int = -32600
METHOD_NOT_FOUND: int = -32601
INVALID_PARAMS: int = -32602
INTERNAL_ERROR: int = -32603
AUTH_ERROR: int = -32001

TOOL_ENDPOINTS: dict[str, tuple[str, str]] = {
    "add_expense": ("POST", "/expenses"),
    "get_budget_status": ("GET", "/dashboard/summary"),
    "monthly_summary": ("GET", "/dashboard/by-category"),
    "list_expenses": ("GET", "/expenses"),
}
"""The FROZEN four-operation map (method, path) the tool modules may call."""


def list_tools() -> list[dict[str, Any]]:
    """Return the four frozen MCP tool definitions (REQ-AI-082, REQ-EXT-038).

    Returns:
        list[dict[str, Any]]: Definitions with strict JSON-schema inputs:
            every property is typed, every non-optional field is listed, and
            no extra key is accepted.
    """
    return [
        {
            "name": "add_expense",
            "description": "Record one expense for the authenticated user.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "amount": {"type": "string", "description": "Decimal string, e.g. 12.50."},
                    "category_id": {"type": "string", "description": "Category uuid."},
                    "date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                    "note": {"type": "string", "description": "Optional free text."},
                },
                "required": ["amount", "category_id", "date"],
                "additionalProperties": False,
            },
        },
        {
            "name": "get_budget_status",
            "description": "Report budget, spend and remaining for one month.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "year_month": {"type": "string", "description": "Month YYYY-MM."},
                },
                "required": ["year_month"],
                "additionalProperties": False,
            },
        },
        {
            "name": "monthly_summary",
            "description": "Return the per-category breakdown for one month.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "year_month": {"type": "string", "description": "Month YYYY-MM."},
                },
                "required": ["year_month"],
                "additionalProperties": False,
            },
        },
        {
            "name": "list_expenses",
            "description": "List recorded expenses with filters and pagination.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "year_month": {"type": "string", "description": "Optional month filter."},
                    "category_id": {"type": "string", "description": "Optional category filter."},
                    "page": {"type": "integer", "minimum": 1, "description": "1-based page."},
                    "page_size": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Rows per page.",
                    },
                },
                "required": ["page", "page_size"],
                "additionalProperties": False,
            },
        },
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Verify the caller, then dispatch to the matching tool module.

    The JWT check happens BEFORE any import or dispatch, so an unverified
    caller can never reach a tool module (REQ-AI-082).

    Args:
        name: Tool name from the frozen inventory.
        arguments: Validated-by-the-module argument object.

    Returns:
        dict[str, Any]: The tool module's content payload.

    Raises:
        AuthError: The bearer token is missing or not a valid access token.
        ValueError: The tool name is unknown.
    """
    verify_jwt(get_user_token())

    if name not in TOOL_ENDPOINTS:
        raise ValueError(f"unknown tool: {name}")

    module = importlib.import_module(f"tools.{name}")
    run = getattr(module, "run", None)
    if run is None:
        raise ValueError(f"tool module has no run(): {name}")

    result: Any = run(arguments, TOOL_ENDPOINTS[name], MCP_API_BASE_URL)
    return cast(dict[str, Any], result)


def _result(req_id: Any, payload: dict[str, Any]) -> str:
    """Render a JSON-RPC success line for *req_id*."""
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": payload}) + "\n"


def _error(req_id: Any, code: int, message: str) -> str:
    """Render a JSON-RPC error line for *req_id*."""
    body: dict[str, Any] = {"code": code, "message": message}
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": body}) + "\n"


def handle_request(request: dict[str, Any]) -> str:
    """Answer one parsed JSON-RPC *request* with one response line."""
    req_id: Any = request.get("id")
    method = str(request.get("method", ""))

    if method == "initialize":
        return _result(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method == "tools/list":
        return _result(req_id, {"tools": list_tools()})
    if method == "tools/call":
        params = cast(dict[str, Any], request.get("params") or {})
        name = str(params.get("name", ""))
        args = cast(dict[str, Any], params.get("arguments") or {})
        try:
            content = call_tool(name, args)
        except AuthError as exc:
            return _error(req_id, AUTH_ERROR, str(exc))
        except ValueError as exc:
            return _error(req_id, INVALID_PARAMS, str(exc))
        return _result(req_id, {"content": [{"type": "text", "text": json.dumps(content)}]})

    return _error(req_id, METHOD_NOT_FOUND, f"method not found: {method}")


def serve() -> None:
    """Run the newline-delimited stdio loop until stdin reaches EOF."""
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        try:
            request = cast(dict[str, Any], json.loads(text))
        except json.JSONDecodeError:
            sys.stdout.write(_error(None, PARSE_ERROR, "parse error"))
            sys.stdout.flush()
            continue
        except TypeError:
            sys.stdout.write(_error(None, INVALID_REQUEST, "invalid request"))
            sys.stdout.flush()
            continue

        sys.stdout.write(handle_request(request))
        sys.stdout.flush()


if __name__ == "__main__":
    serve()

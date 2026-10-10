"""The four frozen MCP tool modules and their shared error type (REQ-EXT-034..037).

Each module under this package performs exactly ONE backend API call on one
frozen path/method pair, presents the caller's bearer token, and converts any
non-2xx answer into :class:`McpToolError` (REQ-AI-084). Nothing here talks to a
database, opens a socket of its own, or imports the backend application
(REQ-AI-087, REQ-EXT-030).
"""


class McpToolError(Exception):
    """Raised when a tool's backend call fails or answers non-2xx.

    The type is deliberately narrow: authentication failures keep raising
    ``auth.AuthError`` before dispatch, and guardrail rejections keep raising
    ``ValueError`` before any request, so a caller can always tell the three
    failure classes apart (REQ-AI-084, REQ-AI-093).
    """

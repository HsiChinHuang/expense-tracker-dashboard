"""Environment-driven settings for the MCP server (REQ-EXT-032, REQ-AI-086).

The agent layer talks to the SAME public API with the SAME credentials as the
frontend (REQ-ARCH-002), so this module reads the documented environment
triple -- ``MCP_JWT_SECRET``, ``MCP_API_BASE_URL`` and ``MCP_USER_TOKEN`` --
and re-states the JWT algorithm/issuer/audience constants.

Sharing is deliberately BY VALUE: the three literals below are duplicated from
``backend/app/config.py`` rather than imported, because ``mcp-server/`` must
import nothing from the backend application (REQ-AI-087, REQ-EXT-030). The
ac1 gate asserts the equality of both sides, so a drift on either side is
fatal at verification time instead of silently breaking token acceptance.

No default here is a secret: the values mirror the documented placeholders in
``.env.example`` and the server refuses to authenticate anything until the
operator supplies the real environment (REQ-EXT-033).
"""

import os

MCP_JWT_SECRET: str = os.getenv("MCP_JWT_SECRET", "change-me")
"""Shared HS256 secret; identical to the backend's ``JWT_SECRET``."""

MCP_API_BASE_URL: str = os.getenv("MCP_API_BASE_URL", "http://localhost:8000/api/v1")
"""Base URL of the merged backend API -- the only egress target (REQ-EXT-087)."""

MCP_USER_TOKEN: str = os.getenv("MCP_USER_TOKEN", "")
"""Bearer access token the server presents to the API (REQ-EXT-033)."""

JWT_ALGORITHM: str = "HS256"
"""Signature algorithm, exactly as the merged backend configures it."""

JWT_ISSUER: str = "expense-tracker"
"""Expected ``iss`` claim, exactly as the merged backend issues it."""

JWT_AUDIENCE: str = "expense-tracker-api"
"""Expected ``aud`` claim, exactly as the merged backend mints it."""

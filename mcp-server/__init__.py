"""Expense Tracker MCP server package (REQ-AI-080..088, REQ-EXT-030..039).

The package is a stdio JSON-RPC MCP server whose four tools reach the merged
backend through its PUBLIC API with the caller's own bearer token -- never a
database connection and never an import of the backend application
(REQ-AI-087, REQ-ARCH-002).

Layout: ``config.py``/``auth.py``/``server.py`` are the t31 core; the four
modules under ``tools/`` are this card's dispatch surface, and
``tools/__init__.py`` carries the single ``McpToolError`` type every tool
raises for a failed API call. ``README.md`` documents the tools, the
authentication flow, the three environment variables and the subprocess
launch model (REQ-EXT-039, REQ-AI-086/088).
"""

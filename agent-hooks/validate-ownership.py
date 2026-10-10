"""Ownership guardrail hook (REQ-AI-092, REQ-EXT-022).

Pure check that a resource belongs to the calling user. This module
intentionally contains zero import lines: importing it cannot touch any
other module, the network, or the file system. It raises PermissionError
on any violation and is otherwise side-effect free. See
agent-hooks/README.md for the trigger points.
"""


def validate_ownership(owner_id: object, user_id: object) -> None:
    """Raise PermissionError unless the resource owner is the caller.

    Args:
        owner_id: The user id that owns the resource.
        user_id: The authenticated caller's user id.

    Raises:
        PermissionError: If either id is missing or the ids differ.
    """
    if owner_id is None:
        raise PermissionError("resource has no owner; access denied")
    if user_id is None:
        raise PermissionError("caller identity is missing; access denied")
    if owner_id != user_id:
        raise PermissionError("resource belongs to another user; access denied")

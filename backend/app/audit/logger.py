"""Same-transaction audit writer (REQ-DB-053, REQ-ARCH-022/078, REQ-PROD-021).

Chapter 6 6.11.1 verbatim: ``write_audit_log`` adds the ``AuditLog`` row
to the CALLER's session and never commits ("No commit here; caller
commits"). The caller's single ``commit()`` therefore succeeds or fails
for the business write and the audit row together — an audit failure
rolls the business write back with it (REQ-PROD-021). The function must
never open its own session and never call commit/rollback itself.

The eight parameter names are contractual: Chapter 12 12.7.5's service
example calls the writer with keyword arguments ``db=``, ``user_id=``,
``action=``, ``entity_type=``, ``entity_id=``, ``old_value=``,
``new_value=``, ``ip_address=``, and t13/t14 inherit that call shape.
"""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    user_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    old_value: dict[str, Any] | None,
    new_value: dict[str, Any] | None,
    ip_address: str | None,
) -> None:
    """Add an audit row to the caller's session (no commit, no flush).

    Value-shape direction (Chapter 5 5.7.4/5.7.5, Chapter 12 12.7.2):
    CREATE -> ``old_value`` NULL / ``new_value`` full; UPDATE -> both;
    DELETE -> ``old_value`` full / ``new_value`` NULL. Payload key sets
    are frozen by review_plan W5: expense exactly
    ``{amount, date, category_id, note}``, budget exactly
    ``{amount, year_month}`` (REQ-SEC-062 — never secrets).

    Args:
        db: The CALLER's session; the row joins its transaction.
        user_id: Acting user (``audit_logs.user_id``).
        action: ``CREATE``, ``UPDATE`` or ``DELETE`` (ck_audit_action).
        entity_type: ``expense`` or ``budget`` (ck_audit_entity_type).
        entity_id: Id of the affected row (no FK by design, W5).
        old_value: Pre-change payload, or ``None`` on CREATE.
        new_value: Post-change payload, or ``None`` on DELETE.
        ip_address: Best-effort client IP (``get_client_ip``).

    Returns:
        None: The row is only staged; the caller commits.
    """
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
        )
    )


def get_audit_logger() -> Any:
    """Zero-arg joinable dependency returning the writer itself (REQ-ARCH-022).

    Returns:
        Any: The :func:`write_audit_log` function, so services may
            ``Depends(get_audit_logger)`` or call the function directly.
    """
    return write_audit_log

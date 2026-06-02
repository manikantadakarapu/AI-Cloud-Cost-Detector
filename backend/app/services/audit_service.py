import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log_action(
        self, actor_user_id: str, action: str, tenant_id: str | None = None, target_user_id: str | None = None, details: str | None = None
    ) -> None:
        try:
            audit_log = AuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action=action,
                details=details,
                tenant_id=tenant_id,
            )
            self.db.add(audit_log)
            self.db.commit()
            logger.info(
                "Audit log recorded",
                extra={
                    "extra": {
                        "actor_user_id": actor_user_id,
                        "action": action,
                        "target_user_id": target_user_id,
                        "tenant_id": tenant_id,
                    }
                },
            )
        except Exception:
            logger.exception("Failed to record audit log")
            self.db.rollback()

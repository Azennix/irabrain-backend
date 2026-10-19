from fastapi import Depends

from sqlalchemy.orm import Session

from database.dependencies import get_db

from brain.notification.notification_service import NotificationService

from brain.notification.sqlalchemy_notification_repository import (
    SQLAlchemyNotificationRepository,
)


def get_notification_service(
    db: Session = Depends(get_db),
) -> NotificationService:

    repository = SQLAlchemyNotificationRepository(
        session=db
    )

    return NotificationService(
        repository=repository
    )
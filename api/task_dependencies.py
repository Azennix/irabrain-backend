from fastapi import Depends
from sqlalchemy.orm import Session

from database.dependencies import get_db
from brain.project.sqlalchemy_task_repository import (
    SQLAlchemyProjectTaskRepository,
)
from brain.project.task_service import ProjectTaskService
from brain.notification.notification_publisher import NotificationPublisher
from brain.notification.notification_service import NotificationService
from brain.notification.sqlalchemy_notification_repository import (
    SQLAlchemyNotificationRepository,
)

def get_task_service(
    db: Session = Depends(get_db),
) -> ProjectTaskService:
    repository = SQLAlchemyProjectTaskRepository(db)
    notification_repository = SQLAlchemyNotificationRepository(
        session=db
    )

    notification_service = NotificationService(
        repository=notification_repository
    )

    notification_publisher = NotificationPublisher(
        notification_service=notification_service
    )
    return ProjectTaskService(
        repository=repository,
        notification_publisher=notification_publisher,
    )
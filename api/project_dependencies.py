from fastapi import Depends
from sqlalchemy.orm import Session

from database.dependencies import get_db
from brain.project.project_service import ProjectService
from brain.project.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from brain.project.decision_service import ProjectDecisionService
from brain.project.sqlalchemy_decision_repository import (
    SqlAlchemyProjectDecisionRepository,
)
from brain.notification.notification_publisher import NotificationPublisher
from brain.notification.notification_service import NotificationService
from brain.notification.sqlalchemy_notification_repository import (
    SQLAlchemyNotificationRepository,
)


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:

    repository = SQLAlchemyProjectRepository(
        session=db
    )
    notification_repository = SQLAlchemyNotificationRepository(
        session=db
    )
    notification_service = NotificationService(
        repository=notification_repository
    )
    notification_publisher = NotificationPublisher(
        notification_service=notification_service
    )



    return ProjectService(
        repository=repository,
        notification_publisher=notification_publisher,
    )

def get_project_decision_service(
    db: Session = Depends(get_db),
) -> ProjectDecisionService:
    repository = SqlAlchemyProjectDecisionRepository(db)

    return ProjectDecisionService(repository)
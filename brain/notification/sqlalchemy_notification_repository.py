from datetime import datetime

from sqlalchemy.orm import Session

from database.notification_model import NotificationEntity


class SQLAlchemyNotificationRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
    ):
        notification = NotificationEntity(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            is_read=False,
        )

        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)

        return notification

    def get_all(
        self,
        user_id: int,
    ):
        return (
            self.session.query(NotificationEntity)
            .filter(
                NotificationEntity.user_id == user_id
            )
            .order_by(
                NotificationEntity.created_at.desc()
            )
            .all()
        )

    def get_unread_count(
        self,
        user_id: int,
    ):
        return (
            self.session.query(NotificationEntity)
            .filter(
                NotificationEntity.user_id == user_id,
                NotificationEntity.is_read.is_(False),
            )
            .count()
        )

    def mark_as_read(
        self,
        user_id: int,
        notification_id: int,
    ):
        notification = (
            self.session.query(NotificationEntity)
            .filter(
                NotificationEntity.notification_id == notification_id,
                NotificationEntity.user_id == user_id,
            )
            .first()
        )

        if notification is None:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(notification)

        return notification

    def mark_all_as_read(
        self,
        user_id: int,
    ):
        notifications = (
            self.session.query(NotificationEntity)
            .filter(
                NotificationEntity.user_id == user_id,
                NotificationEntity.is_read.is_(False),
            )
            .all()
        )

        now = datetime.utcnow()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        self.session.commit()

        return len(notifications)

    def delete(
        self,
        user_id: int,
        notification_id: int,
    ):
        notification = (
            self.session.query(NotificationEntity)
            .filter(
                NotificationEntity.notification_id == notification_id,
                NotificationEntity.user_id == user_id,
            )
            .first()
        )

        if notification is None:
            return False

        self.session.delete(notification)
        self.session.commit()

        return True
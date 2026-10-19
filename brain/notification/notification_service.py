from brain.notification.notification_types import NotificationType
class NotificationService:

    def __init__(self, repository):
        self.repository = repository

    def create_notification(
        self,
        user_id,
        type: NotificationType,
        title,
        message,
    ):
        return self.repository.create(
            user_id=user_id,
            type=type.value,
            title=title,
            message=message,
        )

    def get_notifications(
        self,
        user_id: int,
    ):
        return self.repository.get_all(
            user_id=user_id,
        )

    def get_unread_count(
        self,
        user_id: int,
    ):
        return self.repository.get_unread_count(
            user_id=user_id,
        )

    def mark_as_read(
        self,
        user_id: int,
        notification_id: int,
    ):
        return self.repository.mark_as_read(
            user_id=user_id,
            notification_id=notification_id,
        )

    def mark_all_as_read(
        self,
        user_id: int,
    ):
        return self.repository.mark_all_as_read(
            user_id=user_id,
        )

    def delete_notification(
        self,
        user_id: int,
        notification_id: int,
    ):
        return self.repository.delete(
            user_id=user_id,
            notification_id=notification_id,
        )
    def publish(self, event):
        return self.create_notification(
            user_id=event.user_id,
            type=event.type,
            title=event.title,
            message=event.message,
    )
from dataclasses import dataclass

from brain.notification.notification_types import NotificationType


@dataclass(frozen=True)
class NotificationEvent:
    user_id: int
    type: NotificationType
    title: str
    message: str
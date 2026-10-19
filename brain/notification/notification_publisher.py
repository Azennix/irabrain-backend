from brain.notification.notification_event import NotificationEvent
from brain.notification.notification_service import NotificationService


class NotificationPublisher:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def publish(self, event: NotificationEvent):
        return self.notification_service.publish(event)
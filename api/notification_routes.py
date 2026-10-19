from fastapi import APIRouter, Depends, HTTPException

from security.dependencies import get_current_user

from api.notification_dependencies import get_notification_service
from brain.notification.notification_service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("")
def get_notifications(
    current_user=Depends(get_current_user),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    notifications = notification_service.get_notifications(
        user_id=current_user.user_id,
    )

    return {
        "notifications": [
            {
                "notification_id": notification.notification_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
            }
            for notification in notifications
        ]
    }


@router.get("/unread-count")
def get_unread_count(
    current_user=Depends(get_current_user),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    count = notification_service.get_unread_count(
        user_id=current_user.user_id,
    )

    return {
        "unread_count": count,
    }


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user=Depends(get_current_user),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    notification = notification_service.mark_as_read(
        user_id=current_user.user_id,
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    return {
        "notification": {
            "notification_id": notification.notification_id,
            "is_read": notification.is_read,
            "read_at": notification.read_at,
        }
    }


@router.patch("/read-all")
def mark_all_notifications_as_read(
    current_user=Depends(get_current_user),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    count = notification_service.mark_all_as_read(
        user_id=current_user.user_id,
    )

    return {
        "success": True,
        "updated_count": count,
    }


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
):
    deleted = notification_service.delete_notification(
        user_id=current_user.user_id,
        notification_id=notification_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    return {
        "success": True,
    }
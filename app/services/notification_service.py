from typing import List, Optional
from datetime import datetime

from app.models.notification import Notification, NotificationEvent
from app.schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from app.exceptions import ResourceNotFoundException


class NotificationService:
    """Service for managing notifications and events"""

    async def create_notification(self, data: NotificationCreate) -> NotificationRead:
        """Create a new notification"""
        notification = Notification(**data.model_dump())
        await notification.insert()

        return NotificationRead(
            id=str(notification.id),
            user_id=notification.user_id,
            event_type=notification.event_type,
            message=notification.message,
            data=notification.data,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )

    async def notify_all_todos_completed(
        self, user_id: str, completed_count: int
    ) -> NotificationRead:
        """Create notification when user completes all their todos"""
        data = NotificationCreate(
            user_id=user_id,
            event_type=NotificationEvent.ALL_TODOS_COMPLETED,
            message=f"Congratulations! You've completed all {completed_count} of your todos!",
            data={"completed_count": completed_count},
        )
        return await self.create_notification(data)

    async def notify_todo_limit_reached(
        self, user_id: str, limit: int
    ) -> NotificationRead:
        """Create notification when user reaches their todo limit"""
        data = NotificationCreate(
            user_id=user_id,
            event_type=NotificationEvent.TODO_LIMIT_REACHED,
            message=f"You've reached your limit of {limit} open todos. Complete some todos to create new ones.",
            data={"limit": limit},
        )
        return await self.create_notification(data)

    async def notify_user_created(
        self, user_id: str, username: str
    ) -> NotificationRead:
        """Create welcome notification for new user"""
        data = NotificationCreate(
            user_id=user_id,
            event_type=NotificationEvent.USER_CREATED,
            message=f"Welcome to Todo App, {username}! Start by creating your first todo.",
            data={"username": username},
        )
        return await self.create_notification(data)

    async def get_user_notifications(
        self, user_id: str, unread_only: bool = False
    ) -> List[NotificationRead]:
        """Get notifications for a user"""
        query = Notification.find(Notification.user_id == user_id)

        if unread_only:
            query = query.find(Notification.read_at == None)

        notifications = await query.sort(-Notification.created_at).to_list()

        return [
            NotificationRead(
                id=str(n.id),
                user_id=n.user_id,
                event_type=n.event_type,
                message=n.message,
                data=n.data,
                created_at=n.created_at,
                read_at=n.read_at,
            )
            for n in notifications
        ]

    async def mark_notification_as_read(
        self, notification_id: str, user_id: str
    ) -> NotificationRead:
        """Mark a notification as read"""
        notification = await Notification.get(notification_id)

        if not notification:
            raise ResourceNotFoundException("Notification", notification_id)

        # Ensure user can only mark their own notifications as read
        if notification.user_id != user_id:
            raise ResourceNotFoundException("Notification", notification_id)

        notification.read_at = datetime.utcnow()
        await notification.save()

        return NotificationRead(
            id=str(notification.id),
            user_id=notification.user_id,
            event_type=notification.event_type,
            message=notification.message,
            data=notification.data,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )

    async def mark_all_notifications_as_read(self, user_id: str) -> int:
        """Mark all user's notifications as read"""
        notifications = await Notification.find(
            Notification.user_id == user_id, Notification.read_at == None
        ).to_list()

        now = datetime.utcnow()
        count = 0

        for notification in notifications:
            notification.read_at = now
            await notification.save()
            count += 1

        return count

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for user"""
        return await Notification.find(
            Notification.user_id == user_id, Notification.read_at == None
        ).count()

    async def delete_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old notifications (for maintenance)"""
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)

        old_notifications = await Notification.find(
            Notification.created_at < cutoff_date
        ).to_list()

        count = 0
        for notification in old_notifications:
            await notification.delete()
            count += 1

        return count


def get_notification_service() -> NotificationService:
    """Dependency injection factory for NotificationService"""
    return NotificationService()

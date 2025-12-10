from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.notification import NotificationEvent


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""

    user_id: str = Field(..., description="ID of the user this notification belongs to")
    event_type: NotificationEvent = Field(..., description="Type of event")
    message: str = Field(..., description="Human-readable notification message")
    data: Optional[dict] = Field(default=None, description="Additional event data")


class NotificationRead(BaseModel):
    """Schema for reading notification data"""

    id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="ID of the user this notification belongs to")
    event_type: NotificationEvent = Field(..., description="Type of event")
    message: str = Field(..., description="Human-readable notification message")
    data: Optional[dict] = Field(default=None, description="Additional event data")
    created_at: datetime = Field(..., description="When the notification was created")
    read_at: Optional[datetime] = Field(
        default=None, description="When the notification was read"
    )

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """Schema for updating notification (mainly for marking as read)"""

    read_at: Optional[datetime] = Field(
        None, description="When the notification was read"
    )

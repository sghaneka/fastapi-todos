from typing import Optional
from datetime import datetime
from enum import Enum

from beanie import Document
from pydantic import Field


class NotificationEvent(str, Enum):
    ALL_TODOS_COMPLETED = "ALL_TODOS_COMPLETED"
    TODO_LIMIT_REACHED = "TODO_LIMIT_REACHED"
    USER_CREATED = "USER_CREATED"


class Notification(Document):
    """Notification document model for tracking events"""

    user_id: str = Field(..., description="ID of the user this notification belongs to")
    event_type: NotificationEvent = Field(..., description="Type of event")
    message: str = Field(..., description="Human-readable notification message")
    data: Optional[dict] = Field(default=None, description="Additional event data")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the notification was created"
    )
    read_at: Optional[datetime] = Field(
        default=None, description="When the notification was read"
    )

    class Settings:
        name = "notifications"
        use_enum_values = True

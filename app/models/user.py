from typing import Optional
from enum import Enum

from beanie import Document
from pydantic import Field, EmailStr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Document):
    """User document model"""

    email: EmailStr = Field(..., unique=True, description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    is_active: bool = Field(default=True, description="Whether the user is active")

    class Settings:
        name = "users"
        use_enum_values = True  # Store enum values as strings in database

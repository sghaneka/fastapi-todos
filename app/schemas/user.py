from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user"""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    role: Optional[UserRole] = Field(default=UserRole.USER, description="User role")


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Full name"
    )
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")


class UserRead(BaseModel):
    """Schema for reading user data"""

    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether the user is active")

    class Config:
        from_attributes = True

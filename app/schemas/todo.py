from typing import Optional

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """Schema for creating a new todo"""

    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(default=None, description="Todo description")
    # owner_id will be set from authenticated user, not from request


class TodoUpdate(BaseModel):
    """Schema for updating a todo"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Todo title"
    )
    description: Optional[str] = Field(None, description="Todo description")
    completed: Optional[bool] = Field(None, description="Whether the todo is completed")


class TodoRead(BaseModel):
    """Schema for reading todo data"""

    id: str = Field(..., description="Todo ID")
    title: str = Field(..., description="Todo title")
    description: Optional[str] = Field(default=None, description="Todo description")
    completed: bool = Field(..., description="Whether the todo is completed")
    owner_id: str = Field(..., description="ID of the user who owns this todo")

    class Config:
        from_attributes = True

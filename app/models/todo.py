from typing import Optional

from beanie import Document
from pydantic import Field


class Todo(Document):
    """Todo document model"""

    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(default=None, description="Todo description")
    completed: bool = Field(default=False, description="Whether the todo is completed")
    owner_id: str = Field(..., description="ID of the user who owns this todo")

    class Settings:
        name = "todos"  # Mongo collection name

    class Config:
        # For docs/openapi examples
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "owner_id": "507f1f77bcf86cd799439011",
            }
        }

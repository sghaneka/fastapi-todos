from typing import Optional

from beanie import Document
from pydantic import Field


class Todo(Document):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False

    class Settings:
        name = "todos"  # Mongo collection name

    class Config:
        # For docs/openapi examples
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
            }
        }

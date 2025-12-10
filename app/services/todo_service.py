from typing import List, Optional

from fastapi import HTTPException, status

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead


class TodoService:
    """
    Equivalent to a NestJS service that uses a Mongoose model.
    """

    async def create_todo(self, data: TodoCreate) -> TodoRead:
        todo = Todo(**data.model_dump())
        await todo.insert()
        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
        )

    async def list_todos(self) -> List[TodoRead]:
        todos = await Todo.find_all().to_list()
        return [
            TodoRead(
                id=str(t.id),
                title=t.title,
                description=t.description,
                completed=t.completed,
            )
            for t in todos
        ]

    async def get_todo(self, todo_id: str) -> TodoRead:
        todo = await Todo.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found",
            )
        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
        )

    async def update_todo(self, todo_id: str, data: TodoUpdate) -> TodoRead:
        todo = await Todo.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        await todo.save()
        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
        )

    async def delete_todo(self, todo_id: str) -> None:
        todo = await Todo.get(todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found",
            )
        await todo.delete()


# Dependency provider for DI
def get_todo_service() -> TodoService:
    """
    This is like Nest's provider factory.
    FastAPI will call this when injecting TodoService.
    """
    return TodoService()

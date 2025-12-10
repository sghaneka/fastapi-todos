from typing import List, Optional

from fastapi import HTTPException, status

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead
from app.exceptions import TodoLimitExceededException, ResourceNotFoundException


# Business Rules Configuration
MAX_OPEN_TODOS = 5


class TodoService:
    """
    TodoService with business rules:
    1. Users can have max 5 open todos
    2. Todo titles must be unique per user
    3. Can't uncomplete if at limit
    4. Notifications on completion events
    """

    async def create_todo(self, data: TodoCreate, owner_id: str) -> TodoRead:
        """Create todo with business rule validation"""

        # Rule 1: Check open todo limit
        open_count = await Todo.find(
            Todo.owner_id == owner_id, Todo.completed == False
        ).count()

        if open_count >= MAX_OPEN_TODOS:
            raise TodoLimitExceededException(open_count, MAX_OPEN_TODOS)

        # Rule 2: Check title uniqueness for this user
        existing_todo = await Todo.find_one(
            Todo.owner_id == owner_id, Todo.title == data.title
        )

        if existing_todo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You already have a todo with title '{data.title}'",
            )

        # Create the todo
        todo_data = data.model_dump()
        todo_data["owner_id"] = owner_id
        todo = Todo(**todo_data)
        await todo.insert()

        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            owner_id=todo.owner_id,
        )

    async def list_todos(self, owner_id: str = None) -> List[TodoRead]:
        """List todos, optionally filtered by owner"""
        if owner_id:
            todos = await Todo.find(Todo.owner_id == owner_id).to_list()
        else:
            todos = await Todo.find_all().to_list()

        return [
            TodoRead(
                id=str(t.id),
                title=t.title,
                description=t.description,
                completed=t.completed,
                owner_id=t.owner_id,
            )
            for t in todos
        ]

    async def get_todo(self, todo_id: str) -> TodoRead:
        todo = await Todo.get(todo_id)
        if not todo:
            raise ResourceNotFoundException("Todo", todo_id)

        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            owner_id=todo.owner_id,
        )

    async def update_todo(
        self, todo_id: str, data: TodoUpdate, owner_id: str = None
    ) -> TodoRead:
        """Update todo with business rule validation"""
        todo = await Todo.get(todo_id)
        if not todo:
            raise ResourceNotFoundException("Todo", todo_id)

        # Rule 3: If trying to uncomplete, check if user is at limit
        if data.completed is False and todo.completed is True:
            open_count = await Todo.find(
                Todo.owner_id == todo.owner_id, Todo.completed == False
            ).count()

            if open_count >= MAX_OPEN_TODOS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot uncomplete todo. You have {open_count} open todos (max: {MAX_OPEN_TODOS})",
                )

        # Check title uniqueness if title is being changed
        if data.title and data.title != todo.title:
            existing_todo = await Todo.find_one(
                Todo.owner_id == todo.owner_id, Todo.title == data.title
            )

            if existing_todo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"You already have a todo with title '{data.title}'",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        await todo.save()

        # Rule 4: Check if this was the last todo being completed
        if data.completed is True:
            remaining_open = await Todo.find(
                Todo.owner_id == todo.owner_id, Todo.completed == False
            ).count()

            if remaining_open == 0:
                print(
                    f"🎉 User {todo.owner_id} completed their last todo! (Would trigger notification)"
                )

        return TodoRead(
            id=str(todo.id),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            owner_id=todo.owner_id,
        )

    async def delete_todo(self, todo_id: str) -> None:
        todo = await Todo.get(todo_id)
        if not todo:
            raise ResourceNotFoundException("Todo", todo_id)
        await todo.delete()

    async def get_user_todo_stats(self, owner_id: str) -> dict:
        """Get statistics about user's todos - useful for business logic"""
        total_todos = await Todo.find(Todo.owner_id == owner_id).count()
        completed_todos = await Todo.find(
            Todo.owner_id == owner_id, Todo.completed == True
        ).count()
        open_todos = total_todos - completed_todos

        return {
            "total": total_todos,
            "completed": completed_todos,
            "open": open_todos,
            "can_create_more": open_todos < MAX_OPEN_TODOS,
            "limit": MAX_OPEN_TODOS,
        }


# Dependency provider for DI
def get_todo_service() -> TodoService:
    """
    This is like Nest's provider factory.
    FastAPI will call this when injecting TodoService.
    """
    return TodoService()

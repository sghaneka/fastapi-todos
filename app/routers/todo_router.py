from typing import List

from fastapi import APIRouter, Depends, status

from app.schemas import TodoCreate, TodoRead, TodoUpdate
from app.services import TodoService
from app.services.todo_service import get_todo_service

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post(
    "",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    payload: TodoCreate,
    service: TodoService = Depends(get_todo_service),
):
    """
    Create a new todo.
    """
    return await service.create_todo(payload)


@router.get(
    "",
    response_model=List[TodoRead],
)
async def list_todos(
    service: TodoService = Depends(get_todo_service),
):
    """
    Get all todos.
    """
    return await service.list_todos()


@router.get(
    "/{todo_id}",
    response_model=TodoRead,
)
async def get_todo(
    todo_id: str,
    service: TodoService = Depends(get_todo_service),
):
    """
    Get a single todo by ID.
    """
    return await service.get_todo(todo_id)


@router.put(
    "/{todo_id}",
    response_model=TodoRead,
)
async def update_todo(
    todo_id: str,
    payload: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
):
    """
    Update a todo.
    """
    return await service.update_todo(todo_id, payload)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_todo(
    todo_id: str,
    service: TodoService = Depends(get_todo_service),
):
    """
    Delete a todo.
    """
    await service.delete_todo(todo_id)
    return None

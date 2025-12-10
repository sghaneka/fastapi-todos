from typing import List

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService, get_user_service
from app.models.user import UserRole
from app.exceptions import (
    UserAlreadyExistsException,
    ResourceNotFoundException,
    UnauthorizedOperationException,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """
    Create a new user.
    """
    try:
        return await service.create_user(payload)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get(
    "",
    response_model=List[UserRead],
)
async def list_users(
    service: UserService = Depends(get_user_service),
):
    """
    Get all users (admin only).
    For testing: using hardcoded admin role. In real app, this would come from auth.
    """
    try:
        # TODO: Replace with actual user role from authentication
        requesting_role = UserRole.ADMIN  # Hardcoded for testing
        return await service.list_users(requesting_role)
    except UnauthorizedOperationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    """
    Get a user by ID.
    """
    try:
        return await service.get_user_by_id(user_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/email/{email}",
    response_model=UserRead,
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
):
    """
    Get a user by email address.
    """
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found",
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    """
    Update a user.
    For testing: using hardcoded requesting user. In real app, this would come from auth.
    """
    try:
        # TODO: Replace with actual user from authentication
        requesting_user_id = "507f1f77bcf86cd799439011"  # Hardcoded for testing
        requesting_role = UserRole.ADMIN  # Hardcoded for testing

        return await service.update_user(
            user_id, payload, requesting_user_id, requesting_role
        )
    except (ResourceNotFoundException, UnauthorizedOperationException) as e:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if isinstance(e, ResourceNotFoundException)
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=e.message)


@router.post(
    "/{user_id}/deactivate",
    response_model=UserRead,
)
async def deactivate_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    """
    Deactivate a user (admin only).
    For testing: using hardcoded admin role. In real app, this would come from auth.
    """
    try:
        # TODO: Replace with actual user role from authentication
        requesting_role = UserRole.ADMIN  # Hardcoded for testing

        return await service.deactivate_user(user_id, requesting_role)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except UnauthorizedOperationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.get(
    "/{user_id}/permissions",
    response_model=dict,
)
async def check_user_permissions(
    user_id: str,
    required_role: UserRole = None,
    service: UserService = Depends(get_user_service),
):
    """
    Check if a user has required permissions.
    """
    has_permission = await service.check_user_permissions(user_id, required_role)
    return {
        "user_id": user_id,
        "has_permission": has_permission,
        "required_role": required_role.value if required_role else None,
    }

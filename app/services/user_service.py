from typing import List, Optional

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.exceptions import (
    UserAlreadyExistsException,
    ResourceNotFoundException,
    UnauthorizedOperationException,
)


class UserService:
    """Service for managing users with role-based operations"""

    async def create_user(self, data: UserCreate) -> UserRead:
        """Create a new user"""
        # Check if user with email already exists
        existing_user = await User.find_one(User.email == data.email)
        if existing_user:
            raise UserAlreadyExistsException(data.email)

        # Check if username already exists
        existing_username = await User.find_one(User.username == data.username)
        if existing_username:
            raise UserAlreadyExistsException(data.username)

        # Create new user
        user = User(**data.model_dump())
        await user.insert()

        return UserRead(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    async def get_user_by_id(self, user_id: str) -> UserRead:
        """Get user by ID"""
        user = await User.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        return UserRead(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    async def get_user_by_email(self, email: str) -> Optional[UserRead]:
        """Get user by email"""
        user = await User.find_one(User.email == email)
        if not user:
            return None

        return UserRead(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    async def list_users(self, requesting_user_role: UserRole) -> List[UserRead]:
        """List users - only admins can see all users"""
        if requesting_user_role != UserRole.ADMIN:
            raise UnauthorizedOperationException("list", "users")

        users = await User.find_all().to_list()
        return [
            UserRead(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
            )
            for user in users
        ]

    async def update_user(
        self,
        user_id: str,
        data: UserUpdate,
        requesting_user_id: str,
        requesting_user_role: UserRole,
    ) -> UserRead:
        """Update user - users can update themselves, admins can update anyone"""
        user = await User.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        # Check permissions
        if requesting_user_role != UserRole.ADMIN and requesting_user_id != user_id:
            raise UnauthorizedOperationException("update", "user")

        # Only admins can change roles
        if data.role is not None and requesting_user_role != UserRole.ADMIN:
            raise UnauthorizedOperationException("change role of", "user")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await user.save()

        return UserRead(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    async def deactivate_user(
        self, user_id: str, requesting_user_role: UserRole
    ) -> UserRead:
        """Deactivate user - only admins can do this"""
        if requesting_user_role != UserRole.ADMIN:
            raise UnauthorizedOperationException("deactivate", "user")

        user = await User.get(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)

        user.is_active = False
        await user.save()

        return UserRead(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    async def check_user_permissions(
        self, user_id: str, required_role: UserRole = None
    ) -> bool:
        """Check if user has required permissions"""
        user = await User.get(user_id)
        if not user or not user.is_active:
            return False

        if required_role and user.role != required_role and user.role != UserRole.ADMIN:
            return False

        return True


def get_user_service() -> UserService:
    """Dependency injection factory for UserService"""
    return UserService()

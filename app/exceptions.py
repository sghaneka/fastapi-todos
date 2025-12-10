"""Domain-specific exceptions for business rules"""


class DomainException(Exception):
    """Base exception for domain-specific errors"""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class TodoLimitExceededException(DomainException):
    """Raised when user tries to create more todos than allowed"""

    def __init__(self, current_count: int, max_allowed: int):
        message = f"Cannot create todo. User has {current_count} open todos (max: {max_allowed})"
        super().__init__(message, "TODO_LIMIT_EXCEEDED")
        self.current_count = current_count
        self.max_allowed = max_allowed


class UnauthorizedOperationException(DomainException):
    """Raised when user tries to perform operation they're not allowed to"""

    def __init__(self, operation: str, resource: str = "resource"):
        message = f"User is not authorized to {operation} this {resource}"
        super().__init__(message, "UNAUTHORIZED_OPERATION")
        self.operation = operation
        self.resource = resource


class ResourceNotFoundException(DomainException):
    """Raised when requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists"""

    def __init__(self, identifier: str):
        message = f"User with identifier '{identifier}' already exists"
        super().__init__(message, "USER_ALREADY_EXISTS")
        self.identifier = identifier


class InvalidUserRoleException(DomainException):
    """Raised when trying to assign invalid role to user"""

    def __init__(self, role: str):
        message = f"Invalid user role: '{role}'"
        super().__init__(message, "INVALID_USER_ROLE")
        self.role = role

class EntityAlreadyExists(Exception):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(f"{entity_name} with ID {entity_id} already exists")


class EntityNotFound(Exception):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(f"{entity_name} with ID {entity_id} not found")


class DatabaseError(Exception):
    def __init__(self, func_name: str, detail: str = "Database error"):
        super().__init__(f"{func_name}: {detail}")


class ValidationError(Exception):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail)


class PermissionDenied(Exception):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail)


class InternalServerError(Exception):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail)


class InvalidFunctionName(Exception):
    def __init__(self, func_name: str):
        super().__init__(f"Invalid function name: {func_name}")


class TTIException(Exception):
    """Base exception class for The Things Stack TTI."""

    def __init__(self, message=None):
        super().__init__(message)


class RequestError(Exception):
    def __init__(self, message, original_exception=None):
        self.message = message
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            original_type = type(self.original_exception).__name__
            return f"{self.message} ({original_type})"

        return self.message


class QueueSendError(Exception):
    def __init__(self, message=None):
        super().__init__(message)

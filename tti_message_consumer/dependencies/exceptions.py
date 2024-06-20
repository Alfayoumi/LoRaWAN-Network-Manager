class CalculationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class RabbitMQConnectionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class RabbitMQConsumingError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ProcessError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class DatabaseError(Exception):
    def __init__(self, func_name: str, detail: str = "Database error"):
        super().__init__(f"{func_name}: {detail}")

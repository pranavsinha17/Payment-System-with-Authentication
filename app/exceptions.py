class APIException(Exception):
    def __init__(self, message: str = "API Exception", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class BadRequestException(APIException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message, 400)

class UnauthorizedException(APIException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)

class ForbiddenException(APIException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)

class NotFoundException(APIException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message, 404)

class ConflictException(APIException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, 409)

class UnprocessableEntityException(APIException):
    def __init__(self, message: str = "Unprocessable Entity"):
        super().__init__(message, 422)

class InternalServerErrorException(APIException):
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message, 500) 
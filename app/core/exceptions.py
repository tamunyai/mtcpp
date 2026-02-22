from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail="Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class NotFoundException(AppException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ForbiddenException(AppException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


class UnauthorizedException(AppException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)

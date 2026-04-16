from fastapi import status 
from fastapi import HTTPException

class BaseHTTPException(HTTPException):
    def __init__(
            self,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: str = "Внутренняя ошибка сервера"
            ) -> None:
        self.status_code = status_code
        self.detail = detail 
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )

class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует."
        )

class InvalidCredentialsError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль."
        )

class InvalidTokenError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен."
        )

class ExpiredTokenError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Просроченный токен."
        )

class UserNotFoundError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден."
        )

class PermissionDeniedError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав."
        )

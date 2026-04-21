from fastapi import HTTPException
from fastapi import status 

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

class ExpiredTokenError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Просроченный токен."
        )

class InvalidTokenError(BaseHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен."
        )

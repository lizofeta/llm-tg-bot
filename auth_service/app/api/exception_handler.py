from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import BaseHTTPException

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseHTTPException)
    async def base_http_exception_handler(
        _: Request, e: BaseHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )

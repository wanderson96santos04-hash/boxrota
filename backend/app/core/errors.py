from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


def error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=APIError(code=code, message=message, details=details).model_dump(),
    )


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException):
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        return error_response(500, "internal_error", "Erro interno.", {"type": exc.__class__.__name__})
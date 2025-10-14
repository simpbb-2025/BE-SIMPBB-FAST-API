from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


def _build_error_payload(message: str, *, data: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": data,
    }


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    payload = _build_error_payload(str(exc.detail), data={"status_code": exc.status_code})
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(payload))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = _build_error_payload(
        "Validation failed",
        data={"errors": exc.errors(), "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY},
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder(payload))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    payload = _build_error_payload(
        "Internal server error",
        data={"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(payload))

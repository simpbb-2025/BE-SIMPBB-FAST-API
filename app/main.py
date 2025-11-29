from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.api import errors as api_errors
from app.core.config import settings
from app.core.database import Base, engine

# Import models so that SQLAlchemy registers them with the shared metadata.
from app.modules.users import models as users_models  # noqa: F401
from app.modules.spop import models as spop_models  # noqa: F401
app = FastAPI(title="SIMPBB API", version="0.1.0")

if settings.cors_origins:
    allow_methods = settings.cors_allow_methods or ["*"]
    allow_headers = settings.cors_allow_headers or ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return await api_errors.http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, exc):
    return await api_errors.validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def custom_unhandled_exception_handler(request, exc):
    return await api_errors.unhandled_exception_handler(request, exc)


app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    # Ensure database tables declared in SQLAlchemy metadata exist.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

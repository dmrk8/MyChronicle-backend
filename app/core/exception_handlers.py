from typing import cast
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

logger = structlog.get_logger()


async def app_exception_handler(request: Request, exc: Exception):
    app_exc = cast(AppException, exc)
    if app_exc.status_code >= 500:
        logger.error(
            "app_exception",
            method=request.method,
            url=str(request.url),
            status_code=app_exc.status_code,
            detail=app_exc.detail,
        )
    return JSONResponse(
        status_code=app_exc.status_code, content={"detail": app_exc.detail}
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        method=request.method,
        url=str(request.url),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

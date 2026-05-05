import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

logger = structlog.get_logger()


async def app_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, AppException):
        return await unhandled_exception_handler(request, exc)
    
    if exc.status_code >= 500:
        logger.error(
            "app_exception",
            method=request.method,
            url=str(request.url),
            status_code=exc.status_code,
            detail=exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        method=request.method,
        url=str(request.url),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

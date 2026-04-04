from typing import cast
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: Exception):
    app_exc = cast(AppException, exc)
    return JSONResponse(
        status_code=app_exc.status_code, content={"detail": app_exc.detail}
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


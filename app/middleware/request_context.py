import uuid
from fastapi import Request
from structlog.contextvars import bind_contextvars, clear_contextvars


async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
    finally:
        clear_contextvars()

    response.headers["X-Request-ID"] = request_id
    return response

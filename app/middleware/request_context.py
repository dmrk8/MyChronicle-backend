import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        start_time = time.perf_counter()

        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=client_host,
            user_agent=user_agent,
        )

        try:
            response = await call_next(request)
        except Exception:
            raise
        finally:
            clear_contextvars()

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Latency-MS"] = str(elapsed_ms)
        return response

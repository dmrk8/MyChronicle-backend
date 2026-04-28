
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = structlog.get_logger()
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        
        if endpoint in ["/metrics", "/health"]:
            return await call_next(request)

        method = request.method

        bind_contextvars(
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            client_host=client_host,
            user_agent=user_agent,
        )

        try:
            response = await call_next(request)

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)


            response.headers["X-Request-ID"] = request_id
            response.headers["X-Latency-MS"] = str(elapsed_ms)
            
            logger.info(
                "request_completed",
                status_code=str(response.status_code),
                elapsed_ms=elapsed_ms,
            )

            return response
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            logger.exception(
                "request_failed",
                error=str(e),
                elapsed_ms=elapsed_ms,
            )

            raise e
        finally:
            clear_contextvars()

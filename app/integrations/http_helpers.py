import time
from typing import Optional
import httpx
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import structlog
from app.core.exceptions import UpstreamServiceException
from app.observability.metrics import (
    EXTERNAL_API_FAILURES_TOTAL,
    EXTERNAL_API_LATENCY_SECONDS,
    EXTERNAL_API_REQUESTS_TOTAL,
)

tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()

ACTION_SERVICE_MAP = {
    "search_media": "Anime-Manga",
    "get_media_detail": "Anime-Manga",
    "get_trending_media": "Movies-TV",
    "get_movie_detail": "Movies-TV",
    "get_tv_detail": "Movies-TV",
    "get_discover_movie": "Movies-TV",
    "get_discover_tv": "Movies-TV",
    "fetch_omdb_data": "OMDb",
}


async def perform_request(
    *,
    client: httpx.AsyncClient,
    method: str,
    graphql_query: Optional[dict] = None,
    url: str,
    headers: Optional[dict],
    params: Optional[dict] = None,
    action: str,
    external_source: Optional[str],
    media_type: Optional[str],
):

    request_id = structlog.contextvars.get_contextvars().get("request_id")

    with tracer.start_as_current_span(f"external_api_call: {action}") as span:
        span.set_attribute("external.action", action)
        span.set_attribute("external.source", external_source or "unknown")
        span.set_attribute("media.type", media_type or "unknown")
        span.set_attribute("http.url", url)
        span.set_attribute("http.method", method)

        start = time.perf_counter()

        try:
            if graphql_query:
                response = await client.post(url=url, json=graphql_query)

            else:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                )
            elapsed = time.perf_counter() - start

            EXTERNAL_API_REQUESTS_TOTAL.labels(
                external_source=external_source,
                media_type=media_type,
                action=action,
            ).inc()
            EXTERNAL_API_LATENCY_SECONDS.labels(
                external_source=external_source,
                media_type=media_type,
                action=action,
            ).observe(elapsed)

            response.raise_for_status()

            span.set_attribute("http.status_code", response.status_code)

            logger.debug(
                "upstream_request",
                status="success",
                action=action,
                method=method,
                url=str(url),
                status_code=response.status_code,
                request_id=request_id,
                elapsed_ms=int(elapsed * 1000),
            )

            return response.json()

        except Exception as exc:

            elapsed = time.perf_counter() - start
            EXTERNAL_API_FAILURES_TOTAL.labels(
                external_source=external_source,
                media_type=media_type,
                action=action,
            ).inc()
            EXTERNAL_API_LATENCY_SECONDS.labels(
                external_source=external_source,
                media_type=media_type,
                action=action,
            ).observe(elapsed)

            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))

            logger.exception(
                "upstream_request",
                status="error",
                action=action,
                request_id=request_id,
                elapsed_ms=int(elapsed * 1000),
            )
            service_name = ACTION_SERVICE_MAP.get(action, f"Unknown action: {action}")

            if isinstance(exc, httpx.HTTPStatusError):
                span.set_attribute("http.status_code", exc.response.status_code)
                raise UpstreamServiceException(service_name, exc.response.status_code)
            elif isinstance(exc, httpx.RequestError):
                raise UpstreamServiceException(service_name)
            else:
                raise

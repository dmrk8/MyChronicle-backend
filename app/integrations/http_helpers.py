import time
from typing import Optional
import httpx
import structlog
from app.core.exceptions import UpstreamServiceException

logger = structlog.get_logger()

ACTION_SERVICE_MAP = {
    "get_featured_media": "Anime-Manga",
    "search_media": "Anime-Manga",
    "get_media_detail": "Anime-Manga",
    "get_featured_media_bulk": "Anime-Manga",
    "get_featured_manga_bulk": "Anime-Manga",
    "get_trending_media": "Movies-TV",
    "get_movie_detail": "Movies-TV",
    "get_tv_detail": "Movies-TV",
    "get_discover_movie": "Movies-TV",
    "get_discover_tv": "Movies-TV",
}


async def perform_request(
    *,
    client: httpx.AsyncClient,
    method: str,
    graphql_query: Optional[dict] = None,
    url: str,
    headers: Optional[dict],
    params: Optional[dict] = None,
    action: str
):

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

        response.raise_for_status()
        logger.info(
            "upstream_request",
            status="success",
            action=action,
            method=method,
            url=str(url),
            status_code=response.status_code,
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )

        return response.json()

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "upstream_request",
            status="http_error",
            action=action,
            method=method,
            url=str(url),
            status_code=exc.response.status_code,
            response_text=exc.response.text,
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        service_name = ACTION_SERVICE_MAP.get(action, "External service")
        raise UpstreamServiceException(service_name, exc.response.status_code)

    except httpx.RequestError as exc:
        logger.error(
            "upstream_request",
            status="connection_error",
            action=action,
            method=method,
            url=str(url),
            error=str(exc),
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        service_name = ACTION_SERVICE_MAP.get(action, "External service")
        raise UpstreamServiceException(service_name)
    except Exception:
        logger.exception(
            "upstream_request",
            status="unexpected_error",
            action=action,
            method=method,
            url=str(url),
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        service_name = ACTION_SERVICE_MAP.get(action, "External service")
        raise UpstreamServiceException(service_name)

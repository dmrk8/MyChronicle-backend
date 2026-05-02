import time
from typing import Optional
import httpx

import structlog
from app.core.exceptions import UpstreamServiceException


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
):

    request_id = structlog.contextvars.get_contextvars().get("request_id")

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

        response.raise_for_status()

        logger.info(
            "external_api_call",
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

        logger.exception(
            "external_api_call",
            status="error",
            action=action,
            request_id=request_id,
            elapsed_ms=int(elapsed * 1000),
        )
        service_name = ACTION_SERVICE_MAP.get(action, f"Unknown action: {action}")

        if isinstance(exc, httpx.HTTPStatusError):
            raise UpstreamServiceException(service_name, exc.response.status_code)
        elif isinstance(exc, httpx.RequestError):
            raise UpstreamServiceException(service_name)
        else:
            raise

import time
import httpx
import structlog

logger = structlog.get_logger()


async def perform_request(
    *,
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict,
    params: dict | None = None,
    action: str,
):
    
    start = time.perf_counter()
    try:
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
            elapsed_ms=int((time.perf_counter() - start) * 1000)
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
        raise

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
        raise

    except Exception:
        logger.exception(
            "upstream_request",
            status="unexpected_error",
            action=action,
            method=method,
            url=str(url),
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        raise

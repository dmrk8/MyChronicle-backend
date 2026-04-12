import asyncio
import time
from typing import Awaitable, Callable, TypeVar
from pymongo.errors import PyMongoError
import structlog

T = TypeVar("T")

SLOW_DB_THRESHOLD_MS = 500

async def run_db_op(
    logger: structlog.BoundLogger,
    op: Callable[[], Awaitable[T]],
    *,
    success_event: str,
    error_event: str,
    context: dict,
) -> T:
    start = time.perf_counter()
    try:
        result = await op()
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.debug(
            success_event,
            **context,
            elapsed_ms=elapsed_ms,
        )
        if elapsed_ms > SLOW_DB_THRESHOLD_MS:
            logger.warning(
                "slow_db_operation",
                **context,
                elapsed_ms=elapsed_ms,
            )
        return result
    except asyncio.CancelledError:
        logger.warning("db_operation_cancelled", **context)
        raise
    except PyMongoError as e:
        logger.error(
            error_event,
            **context,
            error=str(e),
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        raise

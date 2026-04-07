import time
from typing import Awaitable, Callable, TypeVar
from pymongo.errors import PyMongoError

T = TypeVar("T")


async def run_db_op(
    logger,
    op: Callable[[], Awaitable[T]],
    *,
    success_event: str,
    error_event: str,
    context: dict,
) -> T:
    start = time.perf_counter()
    try:
        result = await op()
        logger.info(
            success_event,
            **context,
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        return result
    except PyMongoError as e:
        logger.exception(
            error_event,
            **context,
            error=str(e),
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )
        raise

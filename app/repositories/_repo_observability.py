import asyncio
import time
from typing import Awaitable, Callable, TypeVar
from pymongo.errors import PyMongoError
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

from app.models.db.db_context_model import DBOpContext
from app.observability.metrics import (
    MONGO_QUERY_DURATION,
    MONGO_QUERY_FAILURE,
    MONGO_QUERY_SUCCESS,
    MONGO_SLOW_QUERY,
)

T = TypeVar("T")

SLOW_DB_THRESHOLD_MS = 500


async def run_db_op(
    logger: structlog.BoundLogger,
    op: Callable[[], Awaitable[T]],
    *,
    success_event: str,
    error_event: str,
    context: DBOpContext,
) -> T:
    with tracer.start_as_current_span("mongodb.query") as span:
        span.set_attribute("db.system", "mongodb")
        span.set_attribute("db.operation", context.operation)
        span.set_attribute("db.collection", context.collection)

        start = time.perf_counter()

        try:
            result = await op()
            elapsed_ms = int((time.perf_counter() - start) * 1000)

            MONGO_QUERY_DURATION.labels(
                operation=context.operation,
                collection=context.collection,
            ).observe(elapsed_ms / 1000)

            MONGO_QUERY_SUCCESS.labels(
                operation=context.operation,
                collection=context.collection,
            ).inc()

            logger.debug(
                success_event,
                **context.model_dump(exclude_unset=True),
                elapsed_ms=elapsed_ms,
            )
            if elapsed_ms > SLOW_DB_THRESHOLD_MS:
                MONGO_SLOW_QUERY.labels(
                    operation=context.operation,
                    collection=context.collection,
                ).inc()
                logger.warning(
                    "slow_db_operation",
                    **context.model_dump(exclude_unset=True),
                    elapsed_ms=elapsed_ms,
                )

            span.set_attribute("db.duration_ms", elapsed_ms)
            span.set_status(Status(StatusCode.OK))

            return result

        except asyncio.CancelledError:
            logger.warning(
                "db_operation_cancelled", **context.model_dump(exclude_unset=True)
            )
            raise
        
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            
            MONGO_QUERY_FAILURE.labels(
                operation=context.operation,
                collection=context.collection,
            ).inc()

            MONGO_QUERY_DURATION.labels(
                operation=context.operation,
                collection=context.collection,
            ).observe(elapsed_ms / 1000)

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            span.set_attribute("db.duration_ms", elapsed_ms)

            logger.error(
                error_event,
                **context.model_dump(exclude_unset=True),
                error=str(e),
                elapsed_ms=elapsed_ms,
            )
            raise

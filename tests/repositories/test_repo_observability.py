from unittest import mock

import pytest
import structlog
from unittest.mock import AsyncMock, MagicMock, patch
from pymongo.errors import PyMongoError
import asyncio

from app.repositories._repo_observability import run_db_op, SLOW_DB_THRESHOLD_MS
from app.models.db.db_context_model import DBOpContext


@pytest.fixture
def logger():
    mock_logger = MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    return mock_logger


@pytest.fixture
def context():
    return DBOpContext(username="test", operation="op", collection="col")


@pytest.mark.asyncio
async def test_run_db_op_success(logger, context):
    async def op():
        return "ok"

    result = await run_db_op(
        logger, op, success_event="success", error_event="error", context=context
    )
    assert result == "ok"
    logger.info.assert_called_with(
        "success",
        **context.model_dump(exclude_unset=True),
        elapsed_ms=pytest.approx(logger.info.call_args[1]["elapsed_ms"], rel=1e-2)
    )


@pytest.mark.asyncio
async def test_run_db_op_slow_warns(logger, context):
    async def op():
        await asyncio.sleep((SLOW_DB_THRESHOLD_MS + 50) / 1000)
        return "slow"

    await run_db_op(
        logger, op, success_event="success", error_event="error", context=context
    )
    logger.warning.assert_any_call(
        "slow_db_operation",
        **context.model_dump(exclude_unset=True),
        elapsed_ms=pytest.approx(
            logger.warning.call_args.kwargs["elapsed_ms"], rel=1e-2
        )
    )


@pytest.mark.asyncio
async def test_run_db_op_pymongo_error(logger, context):
    async def op():
        raise PyMongoError("fail")

    with pytest.raises(PyMongoError):
        await run_db_op(
            logger, op, success_event="success", error_event="error", context=context
        )
    logger.error.assert_called_with(
        "error",
        **context.model_dump(exclude_unset=True),
        error="fail",
        elapsed_ms=pytest.approx(logger.error.call_args.kwargs["elapsed_ms"], rel=1e-2)
    )


@pytest.mark.asyncio
async def test_run_db_op_cancelled_error(logger, context):
    async def op():
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        await run_db_op(
            logger, op, success_event="success", error_event="error", context=context
        )
    logger.warning.assert_called_with(
        "db_operation_cancelled", **context.model_dump(exclude_unset=True)
    )

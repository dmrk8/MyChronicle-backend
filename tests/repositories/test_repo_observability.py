import pytest
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from app.models.db.db_context_model import DBOpContext

@pytest.fixture
def logger():
    return MagicMock()

@pytest.fixture
def context():
    return DBOpContext(username="test", operation="op", collection="col")


import pytest
from app.repositories._repo_observability import run_db_op, SLOW_DB_THRESHOLD_MS

@pytest.mark.asyncio
async def test_run_db_op_success(logger, context):
    op = AsyncMock(return_value="ok")

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("time.perf_counter", lambda: 1.0)

        # fake elapsed time = 100ms
        calls = [1.0, 1.1]
        mp.setattr("time.perf_counter", lambda: calls.pop(0))

        result = await run_db_op(
            logger,
            op,
            success_event="success",
            error_event="error",
            context=context,
        )

    assert result == "ok"

    logger.info.assert_called_once()
    args, kwargs = logger.info.call_args

    assert args[0] == "success"
    assert kwargs["elapsed_ms"] == 100
    assert kwargs["slow"] is False


import pytest
from app.repositories._repo_observability import SLOW_DB_THRESHOLD_MS

@pytest.mark.asyncio
async def test_run_db_op_slow_warning(logger, context):
    op = AsyncMock(return_value="slow")

    with pytest.MonkeyPatch().context() as mp:
        calls = [1.0, 1.0 + (SLOW_DB_THRESHOLD_MS + 100) / 1000]
        mp.setattr("time.perf_counter", lambda: calls.pop(0))

        await run_db_op(
            logger,
            op,
            success_event="success",
            error_event="error",
            context=context,
        )

    logger.info.assert_called_once()
    args, kwargs = logger.info.call_args

    assert kwargs["slow"] is True


import pytest
from pymongo.errors import PyMongoError

@pytest.mark.asyncio
async def test_run_db_op_pymongo_error(logger, context):
    op = AsyncMock(side_effect=PyMongoError("fail"))

    with pytest.MonkeyPatch().context() as mp:
        calls = [1.0, 1.2]
        mp.setattr("time.perf_counter", lambda: calls.pop(0))

        with pytest.raises(PyMongoError):
            await run_db_op(
                logger,
                op,
                success_event="success",
                error_event="error",
                context=context,
            )

    logger.error.assert_called_once()
    args, kwargs = logger.error.call_args

    assert args[0] == "error"
    assert kwargs["error"] == "fail"
    assert "elapsed_ms" in kwargs


import pytest
import asyncio

@pytest.mark.asyncio
async def test_run_db_op_cancelled(logger, context):
    op = AsyncMock(side_effect=asyncio.CancelledError())

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("time.perf_counter", lambda: 1.0)

        with pytest.raises(asyncio.CancelledError):
            await run_db_op(
                logger,
                op,
                success_event="success",
                error_event="error",
                context=context,
            )

    logger.warning.assert_called_once()
    args, kwargs = logger.warning.call_args

    assert args[0] == "db_operation_cancelled"
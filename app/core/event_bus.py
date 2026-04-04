from collections import defaultdict
from typing import Any, Awaitable, Callable, DefaultDict
import asyncio
import structlog

logger = structlog.get_logger()
Handler = Callable[..., Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: DefaultDict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event: str, handler: Handler) -> None:
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    async def publish(self, event: str, **kwargs: Any) -> None:
        handlers = self._handlers.get(event, [])
        if not handlers:
            logger.warning("no_handlers_for_event", event=event)
            return

        results = await asyncio.gather(
            *(handler(**kwargs) for handler in handlers),
            return_exceptions=True,
        )

        errors = [r for r in results if isinstance(r, Exception)]
        for err in errors:
            logger.error("event_handler_failed", event=event, error=str(err))

        if errors:
            raise ExceptionGroup(f"handlers failed for '{event}'", errors)
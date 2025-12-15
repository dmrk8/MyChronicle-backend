from app.core.config import Settings
import logging
import structlog
from structlog.contextvars import merge_contextvars
from structlog.processors import TimeStamper
from structlog.stdlib import LoggerFactory


def setup_logging(settings: Settings):
    env = settings.env
    log_level = settings.log_level.upper()

    logging.basicConfig(level=log_level)

    shared_processors = [
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        TimeStamper(fmt="iso"),
    ]

    if env == "prod":
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]

    structlog.configure(
        processors=processors,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

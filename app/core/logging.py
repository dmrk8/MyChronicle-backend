from app.core.config import Settings
import logging
import structlog.stdlib

from rich.console import Console
from rich.pretty import Pretty
from rich.text import Text

console = Console()


def serialize_enums(_, __, event_dict):
    for k, v in event_dict.items():
        if hasattr(v, "name"):
            event_dict[k] = v.name
    return event_dict


def rich_renderer(_, __, event_dict):

    timestamp = event_dict.pop("timestamp", "")
    level = event_dict.pop("level", "").upper()
    message = event_dict.pop("event", "")

    level_styles = {
        "DEBUG": "dim",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }

    level_style = level_styles.get(level, "white")

    header = Text()
    header.append(timestamp + " ", style="dim")
    header.append(f"[{level}] ", style=level_style)
    header.append(message, style="bold")

    if event_dict.get("elapsed_ms", 0) > 100:
        header.stylize("bold red")

    console.print(header)

    # Only print details if there are any
    if event_dict:
        console.print(Pretty(event_dict, expand_all=True))

    return ""


def setup_logging(settings: Settings):
    env = settings.env
    log_level = settings.log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to prevent duplicates
    root_logger.handlers = []

    # Create console handler with no formatting
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    root_logger.addHandler(handler)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if env == "prod":
        structlog.configure(
            processors=shared_processors + [structlog.processors.JSONRenderer()],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    else:
        structlog.configure(
            processors=shared_processors + [rich_renderer],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    


from app.core.config import Settings
import logging
import structlog.stdlib

from structlog.contextvars import merge_contextvars
from structlog.processors import TimeStamper
from structlog.stdlib import LoggerFactory


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

    for k, v in event_dict.items():
        line = Text()
        line.append(f"{k}: ", style="bold orange1")
        line.append(str(v), style="white")
        console.print(line)

    if event_dict:
        console.print(Pretty(event_dict, expand_all=True))

    if len(event_dict) <= 3:
        inline = " ".join(f"{k}={v}" for k, v in event_dict.items())
        console.print(f"{header} {inline}")
    else:
        console.print(header)
        console.print(Pretty(event_dict, expand_all=True))

    return ""


def setup_logging(settings: Settings):
    env = settings.env
    log_level = settings.log_level.upper()

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
    )

    shared_processors = [
        structlog.stdlib.filter_by_level,
        merge_contextvars,
        TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if env == "prod":
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        processors = shared_processors + [rich_renderer]

    structlog.configure(
        processors=processors,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

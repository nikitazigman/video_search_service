import typing as tp

from enum import Enum

import pydantic_settings
import structlog

from cdn_worker.settings.base import BaseAppSettings


LoggerProcessors = (
    tp.Iterable[
        tp.Callable[
            [tp.Any, str, tp.MutableMapping[str, tp.Any]],
            tp.Mapping[str, tp.Any]
            | str
            | bytes
            | bytearray
            | tuple[tp.Any, ...],
        ]
    ]
    | None  # noqa: W503
)


class LoggerLevelType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingSettings(BaseAppSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="logging_", use_enum_values=True
    )

    level: LoggerLevelType = LoggerLevelType.INFO

    @property
    def config(self) -> dict[str, tp.Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json_formatter": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                "plain_console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(),
                },
            },
            "handlers": {
                "console": {
                    "level": self.level,
                    "class": "logging.StreamHandler",
                    "formatter": "plain_console",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console"],
                    "level": self.level,
                },
            },
        }


def configure_logger() -> None:
    """Configure structlog logger.


    Returns:
        None.

    Note:
        Async logger should be called within async context.
    """
    shared_processors: LoggerProcessors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

import typing as tp

from enum import Enum

import structlog

from pydantic_settings import SettingsConfigDict

from stream_api.settings.base import BaseAppSettings


LoggerProcessors = (
    tp.Iterable[
        tp.Callable[
            [tp.Any, str, tp.MutableMapping[str, tp.Any]],
            tp.Mapping[str, tp.Any] | str | bytes | bytearray | tuple[tp.Any, ...],
        ]
    ]
    | None
)


class LoggerLevelType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="logging_", use_enum_values=True)

    level: LoggerLevelType = LoggerLevelType.DEBUG

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


def configure_logger(*, enable_async_logger: bool = False) -> None:
    """Configure structlog logger.

    Args:
        enable_async_logger: Enable async logger. Default: False.

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

    logger_wrapper = (
        structlog.stdlib.AsyncBoundLogger
        if enable_async_logger
        else structlog.stdlib.BoundLogger
    )

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=logger_wrapper,
        cache_logger_on_first_use=True,
    )

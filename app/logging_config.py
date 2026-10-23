import json
import logging
import logging.config
import os
import time
import uuid
from contextvars import ContextVar

from fastapi import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# Attributes present on every LogRecord; anything else came from `extra=`
_RESERVED_ATTRS = set(
    vars(logging.LogRecord("", 0, "", 0, "", (), None))
) | {"message", "asctime", "request_id", "taskName"}


def _extra_fields(record: logging.LogRecord) -> dict:
    return {k: v for k, v in vars(record).items() if k not in _RESERVED_ATTRS}


class RequestIdFilter(logging.Filter):
    """Attaches the current request's ID to every log record"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for production log aggregation"""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            **_extra_fields(record),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, default=str)


class TextFormatter(logging.Formatter):
    """Human readable output for local development, extras appended as key=value"""

    def __init__(self):
        super().__init__(
            "%(asctime)s %(levelname)-8s [%(name)s] [%(request_id)s] %(message)s"
        )

    def formatMessage(self, record: logging.LogRecord) -> str:
        line = super().formatMessage(record)
        extras = _extra_fields(record)
        if extras:
            line += " " + " ".join(f"{k}={v}" for k, v in extras.items())
        return line


def configure_logging():
    """
    Configures logging for the whole app. Controlled by:
      LOG_LEVEL  - DEBUG, INFO, WARNING, ... (default INFO)
      LOG_FORMAT - "json" or "text" (default text)
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    formatter = "json" if os.getenv("LOG_FORMAT", "text").lower() == "json" else "text"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": RequestIdFilter}},
            "formatters": {
                "json": {"()": JsonFormatter},
                "text": {"()": TextFormatter},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                    "filters": ["request_id"],
                },
            },
            "root": {"handlers": ["console"], "level": level},
            "loggers": {
                # route uvicorn through our handler so all output is consistent
                "uvicorn": {"handlers": [], "propagate": True},
                "uvicorn.error": {"handlers": [], "propagate": True},
                # request_logging_middleware replaces uvicorn's access log
                "uvicorn.access": {"handlers": [], "propagate": False},
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


access_logger = get_logger("app.access")


async def request_logging_middleware(request: Request, call_next):
    """
    Assigns each request an ID (reusing an incoming X-Request-ID if present),
    makes it available to every log line, and logs the request on completion.
    """
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_var.set(request_id)
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        access_logger.exception(
            "Unhandled exception",
            extra={"method": request.method, "path": request.url.path},
        )
        raise
    else:
        access_logger.info(
            "%s %s %s",
            request.method,
            request.url.path,
            response.status_code,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)

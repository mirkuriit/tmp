import json
import sys

from contextvars import ContextVar
from uuid import UUID, uuid4

from src.config import settings

from loguru import logger
import logging


context_correlation_id: ContextVar[UUID | str | None] = ContextVar(
    "correlation_id", default=None
)
context_request_info: ContextVar[dict | None] = ContextVar(
    "request_info", default=None
)

def disable_sqlalchemy_logs():
    logging.getLogger('sqlalchemy.engine.Engine').disabled = True


def serialize(record):
    subset = {
        "correlation_id" : context_correlation_id.get(),
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "location": {
            "file" : record["file"].path,
            "function" : record["function"],
            "line" : record["line"]
        },
        "message": record["message"] if record["message"] else None,
        "extra":  record["extra"],
        "request_info" : context_request_info.get()
    }
    return json.dumps(subset, default=str)


def patching(record):
    record["base_log"] = serialize(record)

disable_sqlalchemy_logs()
logger.remove(0)
logger = logger.patch(patching)
logger.add(sys.stderr, level=settings.log_level,  format="{base_log}")

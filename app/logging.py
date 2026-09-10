import logging
from logging import Formatter, Filter
from contextvars import ContextVar
import json
import sys
from app.settings import PROJECT_ROOT_DIR

request_id_var = ContextVar("request_id", default="-")

ALLOWED_EXTRAS = (
    "http_method",
    "http_path",
    "status_code",
    "error_message",
    "timestamp_arrival",
)
FORBIDDEN_EXTRAS = ()


class JsonFormater(Formatter):
    def format(self, record):
        log_entry = {
            "logger": record.name,
            "level": record.levelname,
            "request_id": getattr(record, "request_id", request_id_var.get()),
        }

        for key in record.__dict__:
            if key in FORBIDDEN_EXTRAS:
                continue
            elif key in ALLOWED_EXTRAS:
                log_entry[key] = getattr(record, key)
            else:
                continue

        return json.dumps(log_entry)


class RequestIDFilter(Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def setup_logging(level=logging.INFO):
    logger = logging.getLogger()  # noqa
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    # The option for a logs being directed into file is here.
    # file_handler = logging.FileHandler(filename = PROJECT_ROOT_DIR + "/logs/app_log.txt")

    app_logger = logging.getLogger("app")
    stream_handler.addFilter(RequestIDFilter())
    stream_handler.setFormatter(JsonFormater())

    app_logger.addHandler(stream_handler)
    app_logger.setLevel(level)
    app_logger.propagate = False

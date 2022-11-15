import sys
import logging
import logging.config
import uuid
import time

logging.config.dictConfig({"version": 1, "disable_existing_loggers": False})
from collections import deque
from contextlib import contextmanager

MODULE_NAME = "feast_gcp"
# Ref: https://itnext.io/adding-contextual-data-to-python-logging-2597a835b1f4


class LoggingContextHandler:
    def __init__(self):
        self.attributes = deque([{}])

    def add(self, **new_context_vars):
        old_context = self.attributes[0]
        new_context = {**old_context, **new_context_vars}
        self.attributes.appendleft(new_context)

    def get(self, key):
        return self.attributes[0].get(key)

    def remove(self):
        self.attributes.popleft()

    def __str__(self):
        return str(self.attributes)


logging_context_handler = LoggingContextHandler()


@contextmanager
def logging_context(**kwargs):
    logging_context_handler.add(**kwargs)

    yield

    logging_context_handler.remove()


class ContextFilter(logging.Filter):
    def __init__(self):
        super(ContextFilter, self).__init__()

    def filter(self, record):
        record.request_uuid = logging_context_handler.get("request_uuid")
        return True


logger = logging.getLogger(MODULE_NAME)
logger.propagate = False
context_filter = ContextFilter()
logger.addFilter(context_filter)
format_string = "%(asctime)s - %(name)s - ruuid: %(request_uuid)s - %(pathname)s:%(funcName)s - %(levelname)s - %(message)s"
stdout_formatter = logging.Formatter(format_string)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(stdout_formatter)
logger.addHandler(stdout_handler)


def log_time(get_time=False, printer=print):
    def _log_time(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            walltime = te - ts
            if hasattr(method, "__qualname__"):
                method_name = method.__qualname__
            else:
                method_name = method.__name__
            printer(f"{method_name} runtime: {(te - ts):.3f}s")
            if get_time:
                return result, walltime
            else:
                return result

        return timed

    return _log_time


def logging_request_uuid(method):
    def _logging_request_uuid(*args, **kw):
        with logging_context(request_uuid=str(uuid.uuid4())):
            result = method(*args, **kw)
        return result

    return _logging_request_uuid

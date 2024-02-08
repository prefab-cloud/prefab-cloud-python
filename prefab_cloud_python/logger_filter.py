import logging
from structlog import DropEvent


import prefab_cloud_python
import prefab_pb2 as Prefab
from .context import Context

log = logging.getLogger(__name__)

IGNORE_PREFIX = prefab_cloud_python.__name__
LOG_LEVEL_BASE_KEY = "log-level"

LLV = Prefab.LogLevel.Value


prefab_to_python_log_levels = {
    LLV("NOT_SET_LOG_LEVEL"): LLV("DEBUG"),
    LLV("TRACE"): LLV("DEBUG"),
    LLV("DEBUG"): LLV("DEBUG"),
    LLV("INFO"): LLV("INFO"),
    LLV("WARN"): LLV("WARN"),
    LLV("ERROR"): LLV("ERROR"),
    LLV("FATAL"): LLV("FATAL"),
}
python_log_level_name_to_prefab_log_levels = {
    "debug": LLV("DEBUG"),
    "info": LLV("INFO"),
    "warn": LLV("WARN"),
    "warning": LLV("WARN"),
    "error": LLV("ERROR"),
    "critical": LLV("FATAL"),
}

python_to_prefab_log_levels = {
    logging.DEBUG: LLV("DEBUG"),
    logging.INFO: LLV("INFO"),
    logging.WARN: LLV("WARN"),
    logging.ERROR: LLV("ERROR"),
    logging.CRITICAL: LLV("FATAL"),
}


def iterate_dotted_string(s: str):
    parts = s.split(".")
    for i in range(len(parts), 0, -1):
        yield ".".join(parts[:i])


class LoggerFilter(logging.Filter):
    def __init__(self, client=None) -> None:
        """Filter for use with standard logging. Will get its client reference from prefab_python_client.get_client() unless overridden"""
        super().__init__()
        self.client = client

    def _get_client(self) -> "prefab_cloud_python.Client":
        if self.client:
            return self.client
        return prefab_cloud_python.get_client()

    def filter(self, record: logging.LogRecord) -> bool:
        """this method is used with the standard logger"""
        # prevent recursion
        if self._should_skip_processing(record.name):
            return True
        called_method_level = python_to_prefab_log_levels.get(record.levelno)
        if not called_method_level:
            return True
        client = self._get_client()
        if client and client.is_ready():
            client.record_log(record.name, called_method_level)
            return self._should_log_message(record.name, called_method_level)
        return True

    def processor(self, logger, method_name: str, event_dict):
        """this method is used with structlogger.
        It depends on structlog.stdlib.add_log_level being in the structlog pipeline first
        """
        logger_name = getattr(logger, "name", None) or event_dict.get("logger")
        if self._should_skip_processing(logger_name):
            return event_dict
        called_method_level = python_log_level_name_to_prefab_log_levels.get(
            event_dict.get("level")
        )
        if not called_method_level:
            return event_dict
        client = self._get_client()
        if client and client.is_ready():
            client.record_log(logger_name, called_method_level)
            if not self._should_log_message(logger_name, called_method_level):
                raise DropEvent
        return event_dict

    def _should_skip_processing(self, logger_name):
        return logger_name and logger_name.startswith(IGNORE_PREFIX)

    def _should_log_message(self, logger_name, called_method_level):
        closest_log_level = self._get_severity(logger_name)
        return called_method_level >= closest_log_level

    def _get_severity(self, logger_name):
        context = Context.get_current() or {}
        default = LLV("WARN")
        if logger_name:
            full_lookup_key = ".".join([LOG_LEVEL_BASE_KEY, logger_name])
        else:
            full_lookup_key = LOG_LEVEL_BASE_KEY

        for lookup_key in iterate_dotted_string(full_lookup_key):
            log_level = self._get_client().get(
                lookup_key, default=None, context=context
            )
            if log_level:
                return prefab_to_python_log_levels[log_level]

        return default

import logging
import prefab_pb2 as Prefab
from .context import Context

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
    def __init__(self, config_client):
        super().__init__()
        self.config_client = config_client

    def filter(self, record):
        called_method_level = python_to_prefab_log_levels.get(record.levelno)
        if not called_method_level:
            return True
        self.config_client.record_log(record.name, called_method_level)
        return self.should_log_message(record.name, called_method_level)

    def should_log_message(self, logger_name, called_method_level):
        closest_log_level = self.get_severity(logger_name)
        return called_method_level >= closest_log_level

    def get_severity(self, logger_name):
        context = Context.get_current() or {}
        default = LLV("WARN")
        if logger_name:
            full_lookup_key = ".".join([LOG_LEVEL_BASE_KEY, logger_name])
        else:
            full_lookup_key = LOG_LEVEL_BASE_KEY

        for lookup_key in iterate_dotted_string(full_lookup_key):
            log_level = self.config_client.get(
                lookup_key, default=None, context=context
            )
            if log_level:
                return prefab_to_python_log_levels[log_level]

        return default

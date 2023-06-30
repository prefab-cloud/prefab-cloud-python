import os
import re
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
python_to_prefab_log_levels = {
    "debug": LLV("DEBUG"),
    "info": LLV("INFO"),
    "warn": LLV("WARN"),
    "warning": LLV("WARN"),
    "error": LLV("ERROR"),
    "critical": LLV("FATAL"),
}


class LoggerFilter:
    def __init__(self, config_client, log_boundary=None, prefix=None):
        self.config_client = config_client
        self.log_boundary = log_boundary
        self.prefix = prefix

    def filter(self, record):
        path = self.get_path(
            record.pathname, record.funcName, self.prefix, self.log_boundary
        )
        record.msg = "{path}: {msg}".format(path=path, msg=record.getMessage())
        return self.should_log_message(record, path)

    def get_path(self, path, func_name):  # , prefix=None, log_boundary=None):
        if "site-packages" in path:
            path = path.split("site-packages/")[-1]
        else:
            if self.log_boundary is not None:
                path = path.replace(self.log_boundary, "")
            else:
                path = path.replace(os.environ.get("HOME"), "")
            path = [segment for segment in path.split("/") if segment]
            path = ".".join(path)

        path = path.lower()
        path = re.sub(".pyc?$", "", path)
        path = re.sub("-", "_", path)

        if isinstance(self.prefix, str):
            return "%s.%s.%s" % (self.prefix, path, func_name)
        else:
            return "%s.%s" % (path, func_name)

    def should_log_message(self, record, path):
        called_method_level = python_to_prefab_log_levels[record.levelname.lower()]
        closest_log_level = self.get_severity(path)
        return called_method_level >= closest_log_level

    def get_severity(self, location):
        context = Context.get_current() or {}
        default = LLV("WARN")
        closest_log_level = self.config_client.get(
            LOG_LEVEL_BASE_KEY, default=default, context=context
        )

        path_segs = location.split(".")
        for i, _ in enumerate(path_segs):
            next_search_path = ".".join([LOG_LEVEL_BASE_KEY, *path_segs[: i + 1]])
            next_level = self.config_client.get(
                next_search_path, default=closest_log_level, context=context
            )
            if next_level is not None:
                closest_log_level = next_level
        return prefab_to_python_log_levels[closest_log_level]

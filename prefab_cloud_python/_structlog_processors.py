from .context import Context
import prefab_pb2 as Prefab
import re
import os
from structlog import DropEvent
from structlog.processors import CallsiteParameter
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_PREFAB_CONFIG_CLIENT
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_LOG_PREFIX
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_LOG_BOUNDARY
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_PATH_AGGREGATOR
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_SKIP_AGGREGATOR
from ._internal_constants import STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH

LOG_LEVEL_BASE_KEY = "log-level"
LOCATION_KEY = "location"

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


def clean_event_dict(_, __, event_dict):
    event_dict.pop(CallsiteParameter.PATHNAME.value)
    event_dict.pop(CallsiteParameter.FUNC_NAME.value)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_PREFAB_CONFIG_CLIENT)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_LOG_PREFIX)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_LOG_BOUNDARY)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_PATH_AGGREGATOR)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_SKIP_AGGREGATOR)
    event_dict.pop(STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH)
    return event_dict


def set_location(_, __, event_dict):
    # STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH when logging is internal, internal logging, defaults to None
    # presence check needed first to determine if logging is "internal" then check if not-None
    if STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH in event_dict:
        if event_dict[STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH]:
            event_dict[LOCATION_KEY] = (
                "cloud.prefab.client.python.%s"
                % event_dict[STRUCTLOG_EVENT_DICT_KEY_INTERNAL_PATH]
            )
        else:
            event_dict[LOCATION_KEY] = "cloud.prefab.client.python"
    else:
        event_dict[LOCATION_KEY] = get_path(
            event_dict[CallsiteParameter.PATHNAME.value],
            event_dict[CallsiteParameter.FUNC_NAME.value],
            event_dict[STRUCTLOG_EVENT_DICT_KEY_LOG_PREFIX],
            event_dict[STRUCTLOG_EVENT_DICT_KEY_LOG_BOUNDARY],
        )
    return event_dict


def log_or_drop(_, method, event_dict):
    location = event_dict[LOCATION_KEY]
    config_client = event_dict[STRUCTLOG_EVENT_DICT_KEY_PREFAB_CONFIG_CLIENT]
    closest_log_level = get_severity(location, config_client)
    called_method_level = python_to_prefab_log_levels[method]

    if (
        event_dict[STRUCTLOG_EVENT_DICT_KEY_PATH_AGGREGATOR]
        and not event_dict[STRUCTLOG_EVENT_DICT_KEY_SKIP_AGGREGATOR]
    ):
        event_dict[STRUCTLOG_EVENT_DICT_KEY_PATH_AGGREGATOR].push(
            event_dict[LOCATION_KEY], Prefab.LogLevel.Name(called_method_level)
        )

    if closest_log_level > called_method_level:
        raise DropEvent

    return event_dict


def get_severity(location, config_client):
    context = Context.get_current() or {}
    default = Prefab.LogLevel.Value("WARN")
    closest_log_level = config_client.get(
        LOG_LEVEL_BASE_KEY, default=default, context=context
    )

    path_segs = location.split(".")
    for i, _ in enumerate(path_segs):
        next_search_path = ".".join([LOG_LEVEL_BASE_KEY, *path_segs[: i + 1]])
        next_level = config_client.get(
            next_search_path, default=closest_log_level, context=context
        )
        if next_level is not None:
            closest_log_level = next_level
    return prefab_to_python_log_levels[closest_log_level]


def get_path(path, func_name, prefix=None, log_boundary=None):
    if "site-packages" in path:
        path = path.split("site-packages/")[-1]
    else:
        if log_boundary is not None:
            path = path.replace(log_boundary, "")
        else:
            path = path.replace(os.environ.get("HOME"), "")
        path = [segment for segment in path.split("/") if segment]
        path = ".".join(path)

    path = path.lower()
    path = re.sub(".pyc?$", "", path)
    path = re.sub("-", "_", path)

    if isinstance(prefix, str):
        return "%s.%s.%s" % (prefix, path, func_name)
    else:
        return "%s.%s" % (path, func_name)

import logging
from typing import Optional

from structlog import DropEvent

import prefab_cloud_python
from prefab_cloud_python import Client


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
        client = self._get_client()
        if client:
            client.record_log(record.name, record.levelno)
            return self._should_log_message(client, record.name, record.levelno)
        return True

    def processor(self, logger, method_name: str, event_dict):
        """this method is used with structlogger.
        It depends on structlog.stdlib.add_log_level being in the structlog pipeline first
        """
        logger_name = getattr(logger, "name", None) or event_dict.get("logger")
        called_method_level = self._derive_structlog_numeric_level(
            method_name, event_dict
        )
        if not called_method_level:
            return event_dict
        client = self._get_client()
        if client:
            client.record_log(logger_name, called_method_level)
            if not self._should_log_message(client, logger_name, called_method_level):
                raise DropEvent
        return event_dict

    def _derive_structlog_numeric_level(self, method_name, event_dict) -> Optional[int]:
        numeric_level_from_dict = event_dict.get(
            "level_number"
        )  # added by level_to_number processor, if active
        if type(numeric_level_from_dict) == int:
            return numeric_level_from_dict
        string_level = event_dict.get("level") or method_name
        # remap these levels per https://github.com/hynek/structlog/blob/main/src/structlog/_log_levels.py#L66C3-L71C30
        if string_level == "warn":
            # The stdlib has an alias
            string_level = "warning"
        elif string_level == "exception":
            # exception("") method is the same as error("", exc_info=True)
            string_level = "error"

        if string_level:
            maybe_numeric_level = logging.getLevelName(string_level.upper())
            if type(maybe_numeric_level) == int:
                return maybe_numeric_level
        return None

    def _should_log_message(
        self, client: Client, logger_name: str, called_method_level: int
    ):
        closest_log_level = client.get_loglevel(logger_name)
        return called_method_level >= closest_log_level

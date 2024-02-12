import logging
from structlog import DropEvent

import prefab_cloud_python


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
        called_method_level = event_dict.get("level")

        if not called_method_level:
            return event_dict
        client = self._get_client()
        if client:
            client.record_log(logger_name, called_method_level)
            if not self._should_log_message(client, logger_name, called_method_level):
                raise DropEvent
        return event_dict

    def _should_log_message(self, client, logger_name, called_method_level):
        closest_log_level = client.get_loglevel(logger_name)
        return called_method_level >= closest_log_level

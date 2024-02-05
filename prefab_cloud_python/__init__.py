from .options import Options as Options
from .context import Context as Context
from .client import Client as Client
from .logger_filter import LoggerFilter as LoggerFilter
from ._internal_setup import create_prefab_structlog_processor
from ._internal_setup import default_structlog_setup
from .constants import STRUCTLOG_CALLSITE_IGNORES
from importlib.metadata import version
from .read_write_lock import ReadWriteLock
import logging


__base_client = None
__options = None
__lock = ReadWriteLock()


def set_options(options: Options) -> None:
    global __base_client
    global __options
    global __lock
    with __lock.write_locked():
        __options = options


def get() -> Client:
    global __base_client
    global __options
    global __lock
    with __lock.read_locked():
        if __base_client:
            return __base_client

    with __lock.write_locked():
        if not __options:
            raise Exception("Options has not been set")
        if not __base_client:
            logging.info(
                f"Initializing Prefab client version f{version('prefab-cloud-python')}"
            )
            __base_client = Client(__options)
            return __base_client


def reset_instance() -> None:
    """clears the client instance so it will be recreated on the next get() call"""
    global __base_client
    with __lock.write_locked():
        old_client = __base_client
        __base_client = None
        old_client.close()

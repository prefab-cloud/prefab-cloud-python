from typing import Optional

from .options import Options as Options
from .client import Client as Client
from .logger_filter import LoggerFilter as LoggerFilter
from importlib.metadata import version
from .read_write_lock import ReadWriteLock
from ._internal_logging import InternalLogger

log = InternalLogger(__name__)


__base_client: Optional[Client] = None
__options: Optional[Options] = None
__lock = ReadWriteLock()


def set_options(options: Options) -> None:
    """Configure the client. Client will be instantiated lazily with these options. Setting them again will have no effect unless reset_instance is called"""
    global __options
    with __lock.write_locked():
        __options = options


def get_client() -> Client:
    """Returns the singleton instance of the client. Created if needed using the options set by set_options"""
    global __base_client
    with __lock.read_locked():
        if __base_client:
            return __base_client

    with __lock.write_locked():
        if not __options:
            raise Exception("Options has not been set")
        if not __base_client:
            log.info(
                f"Initializing Prefab client version f{version('prefab-cloud-python')}"
            )
            __base_client = Client(__options)
            return __base_client


def reset_instance() -> None:
    """clears the singleton client instance so it will be recreated on the next get() call"""
    global __base_client
    with __lock.write_locked():
        old_client = __base_client
        __base_client = None
        if old_client:
            old_client.close()

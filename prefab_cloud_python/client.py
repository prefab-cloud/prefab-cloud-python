from __future__ import annotations
import functools
import threading
import logging

from urllib3 import Retry

from ._telemetry import TelemetryManager
from .context import Context, ScopedContext
from .config_client import ConfigClient
from .feature_flag_client import FeatureFlagClient
from .logger_filter import LoggerFilter
from .options import Options
from ._requests import TimeoutHTTPAdapter
from typing import Optional, Union
import prefab_pb2 as Prefab
import uuid
import requests
from urllib.parse import urljoin
from importlib.metadata import version

ConfigValueType = Optional[Union[int, float, bool, str, list[str]]]
PostBodyType = Union[Prefab.Loggers, Prefab.ContextShapes, Prefab.TelemetryEvents]
Version = version("prefab-cloud-python")
VersionHeader = "X-PrefabCloud-Client-Version"
logger = logging.getLogger(__name__)


class Client:
    max_sleep_sec = 10
    base_sleep_sec = 0.5
    no_default_provided = "NO_DEFAULT_PROVIDED"

    def __init__(self, options: Options) -> None:
        self.shutdown_flag = threading.Event()
        self.options = options
        self.instance_hash = str(uuid.uuid4())
        self.telemetry_manager = TelemetryManager(self, options)
        if not options.is_local_only():
            self.telemetry_manager.start_periodic_sync()

        self.namespace = options.namespace
        self.api_url = options.prefab_api_url
        # Define the retry strategy
        retry_strategy = Retry(
            total=2,  # Maximum number of retries
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
            allowed_methods=["POST"],
        )
        # Create an TimeoutHTTPAdapter adapter with the retry strategy and a standard timeout and mount it to session
        adapter = TimeoutHTTPAdapter(max_retries=retry_strategy, timeout=5)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers.update({VersionHeader: f"prefab-cloud-python-{Version}"})
        if options.is_local_only():
            logger.info(f"Prefab {Version} running in local-only mode")
        else:
            logger.info(
                f"Prefab {Version} connecting to %s, secure %s"
                % (
                    options.prefab_api_url,
                    options.http_secure,
                ),
            )

        self.context().clear()
        self.config_client()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get(
        self,
        key: str,
        default: ConfigValueType = "NO_DEFAULT_PROVIDED",
        context: str | Context = "NO_CONTEXT_PROVIDED",
    ) -> ConfigValueType:
        if self.is_ff(key):
            if default == "NO_DEFAULT_PROVIDED":
                default = None
            return self.feature_flag_client().get(
                key, default=default, context=self.resolve_context_argument(context)
            )
        else:
            return self.config_client().get(
                key, default=default, context=self.resolve_context_argument(context)
            )

    def enabled(
        self, feature_name: str, context: str | Context = "NO_CONTEXT_PROVIDED"
    ) -> bool:
        return self.feature_flag_client().feature_is_on_for(
            feature_name, context=self.resolve_context_argument(context)
        )

    def is_ff(self, key: str) -> bool:
        raw = self.config_client().config_resolver.raw(key)
        if raw is not None and raw.config_type == Prefab.ConfigType.Value(
            "FEATURE_FLAG"
        ):
            return True
        return False

    def resolve_context_argument(self, context: str | Context) -> Context:
        if context != "NO_CONTEXT_PROVIDED":
            return context
        return Context.get_current()

    def context(self) -> Context:
        return Context.get_current()

    @staticmethod
    def scoped_context(context: dict | Context) -> ScopedContext:
        return Context.scope(context)

    @functools.cache
    def config_client(self) -> ConfigClient:
        client = ConfigClient(self)
        return client

    @functools.cache
    def feature_flag_client(self) -> FeatureFlagClient:
        return FeatureFlagClient(self)

    def post(self, path: str, body: PostBodyType) -> requests.models.Response:
        headers = {
            "Content-Type": "application/x-protobuf",
            "Accept": "application/x-protobuf",
        }

        endpoint = urljoin(self.options.prefab_api_url or "", path)

        return self.session.post(
            endpoint,
            headers=headers,
            data=body.SerializeToString(),
            auth=("authuser", self.options.api_key or ""),
        )

    def record_log(self, path, severity):
        if self.telemetry_manager:
            self.telemetry_manager.record_log(path, severity)

    def logging_filter(self):
        return LoggerFilter(
            self.config_client(),
            prefix=self.options.log_prefix,
            log_boundary=self.options.log_boundary,
        )

    def is_ready(self) -> bool:
        return self.config_client().is_ready()

    def close(self) -> None:
        if not self.shutdown_flag.is_set():
            logging.info("Shutting down prefab client instance")
            self.shutdown_flag.set()
            self.config_client().close()
        else:
            logging.warning("Close already called")

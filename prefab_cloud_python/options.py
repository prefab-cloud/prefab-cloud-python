import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Union


class MissingApiKeyException(Exception):
    """
    Raised when no API key is found
    """

    def __init__(self) -> None:
        super().__init__("No API key found")


class InvalidApiKeyException(Exception):
    """
    Raised when an invalid API key is provided
    """

    def __init__(self, api_key: str) -> None:
        super().__init__(f"Invalid API key: {api_key}")


class InvalidApiUrlException(Exception):
    """
    Raised when an invalid API URL is given
    """

    def __init__(self, url: str) -> None:
        super().__init__(f"Invalid API URL found: {url}")


class InvalidGrpcUrlException(Exception):
    """
    Raised when an invalid gRPC URL is given
    """

    def __init__(self, url: str) -> None:
        super().__init__(f"Invalid gRPC URL found: {url}")


VALID_DATASOURCES = ("LOCAL_ONLY", "ALL")
VALID_ON_NO_DEFAULT = ("RAISE", "RETURN_NONE")
VALID_ON_CONNECTION_FAILURE = ("RETURN", "RAISE")


class Options:
    def __init__(
        self,
        api_key: Optional[str] = None,
        prefab_api_url: Optional[str] = None,
        prefab_grpc_url: Optional[str] = None,
        prefab_datasources: Optional[str] = None,
        logdev: str = "STDIO",
        log_prefix: Optional[str] = None,
        log_boundary: Optional[str] = None,
        namespace: str = "",
        connection_timeout_seconds: int = 10,
        prefab_config_override_dir: Optional[str] = os.environ.get("HOME"),
        prefab_config_classpath_dir: str = ".",
        prefab_envs: list[str] = [],
        http_secure: Optional[bool] = None,
        on_no_default: str = "RAISE",
        on_connection_failure: str = "RETURN",
        collect_logs: bool = True,
        collect_max_paths: int = 1000,
        collect_max_shapes: int = 10_000,
        collect_sync_interval: Optional[int] = None,
    ) -> None:
        self.prefab_datasources = Options.__validate_datasource(prefab_datasources)
        self.__set_api_key(api_key or os.environ.get("PREFAB_API_KEY"))
        self.__set_api_url(
            prefab_api_url
            or os.environ.get("PREFAB_API_URL")
            or "https://api.prefab.cloud"
        )
        self.__set_grpc_url(
            prefab_grpc_url or os.getenv("PREFAB_GRPC_URL") or "grpc.prefab.cloud:443"
        )
        self.logdev = logdev
        self.log_prefix = log_prefix
        self.log_boundary = str(Path(log_boundary).resolve()) if log_boundary else None
        self.namespace = namespace
        self.connection_timeout_seconds = connection_timeout_seconds
        self.prefab_config_override_dir = prefab_config_override_dir
        self.prefab_config_classpath_dir = prefab_config_classpath_dir
        self.http_secure = http_secure or os.environ.get("PREFAB_CLOUD_HTTP") != "true"
        self.prefab_envs = Options.__construct_prefab_envs(prefab_envs)
        self.stats = None
        self.shared_cache = None
        self.__set_url_for_api_cdn()
        self.__set_on_no_default(on_no_default)
        self.__set_on_connection_failure(on_connection_failure)
        self.__set_log_collection(collect_logs, collect_max_paths, self.is_local_only())
        self.collect_sync_interval = collect_sync_interval
        self.collect_max_shapes = collect_max_shapes

    def is_local_only(self) -> bool:
        return self.prefab_datasources == "LOCAL_ONLY"

    def __set_url_for_api_cdn(self) -> None:
        if self.prefab_datasources == "LOCAL_ONLY":
            self.url_for_api_cdn = None
        else:
            cdn_url_from_env = os.environ.get("PREFAB_CDN_URL")
            if cdn_url_from_env is not None:
                self.url_for_api_cdn = cdn_url_from_env
            elif self.prefab_api_url:
                self.url_for_api_cdn = (
                    self.prefab_api_url.replace(".", "-") + ".global.ssl.fastly.net"
                )
            else:
                self.url_for_api_cdn = None  # TODO: should we warn?

    @staticmethod
    def __validate_datasource(datasource: Optional[str]) -> str:
        if os.getenv("PREFAB_DATASOURCES") == "LOCAL_ONLY":
            default = "LOCAL_ONLY"
        else:
            default = "ALL"

        if datasource in VALID_DATASOURCES:
            return datasource
        else:
            return default

    def __set_api_key(self, api_key: Optional[str]) -> None:
        if self.prefab_datasources == "LOCAL_ONLY":
            self.api_key = None
            return

        if api_key is None:
            raise MissingApiKeyException()
        api_key = str(api_key)
        if "-" not in api_key:
            raise InvalidApiKeyException(api_key)
        self.api_key = api_key

    def __set_api_url(self, api_url: Optional[str]) -> None:
        if self.prefab_datasources == "LOCAL_ONLY":
            self.prefab_api_url = None
            return

        api_url = str(api_url)
        parsed_url = urlparse(api_url)
        if parsed_url.scheme in ["http", "https"]:
            self.prefab_api_url = api_url.rstrip("/")
        else:
            raise InvalidApiUrlException(api_url)

    def __set_grpc_url(self, grpc_url: Optional[str]) -> None:
        if self.prefab_datasources == "LOCAL_ONLY":
            self.prefab_grpc_url = None
            return

        grpc_url = str(grpc_url)
        if grpc_url.startswith("grpc."):
            self.prefab_grpc_url = grpc_url
        else:
            raise InvalidGrpcUrlException(grpc_url)

    @classmethod
    def __construct_prefab_envs(cls, envs_from_input: list[str]) -> list[str]:
        all_envs = cls.__parse_envs(envs_from_input) + cls.__parse_envs(
            os.environ.get("PREFAB_ENVS")
        )
        all_envs.sort()
        return all_envs

    @staticmethod
    def __parse_envs(envs: Optional[Union[list[str], str]]) -> list[str]:
        if isinstance(envs, list):
            return envs
        if isinstance(envs, str):
            return [env.strip() for env in envs.split(",")]
        return []

    def __set_on_no_default(self, value: str) -> None:
        if value in VALID_ON_NO_DEFAULT:
            self.on_no_default = value
        else:
            self.on_no_default = "RAISE"

    def __set_on_connection_failure(self, value: str) -> None:
        if value in VALID_ON_CONNECTION_FAILURE:
            self.on_connection_failure = value
        else:
            self.on_connection_failure = "RETURN"

    def __set_log_collection(
        self, collect_logs: bool, collect_max_paths: int, is_local_only: bool
    ) -> None:
        self.collect_logs = collect_logs
        if not collect_logs or is_local_only:
            self.collect_max_paths = 0
        else:
            self.collect_max_paths = collect_max_paths

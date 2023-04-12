import os
from urllib.parse import urlparse


class MissingApiKeyException(Exception):
    "Raised when no API key is found"

    def __init__(self):
        super().__init__("No API key found")


class InvalidApiKeyException(Exception):
    "Raised when an invalid API key is provided"

    def __init__(self, api_key):
        super().__init__("Invalid API key: %s" % api_key)


class InvalidApiUrlException(Exception):
    "Raised when an invalid API URL is given"

    def __init__(self, url):
        super().__init__("Invalid API URL found: %s" % url)


class InvalidGrpcUrlException(Exception):
    "Raised when an invalid gRPC URL is given"

    def __init__(self, url):
        super().__init__("Invalid gRPC URL found: %s" % url)


class Options:
    def __init__(
        self,
        api_key=None,
        prefab_api_url=None,
        prefab_grpc_url=None,
        prefab_datasources=None,
        logdev="STDIO",
        log_prefix=None,
        namespace="",
        connection_timeout_seconds=10,
        prefab_config_override_dir=os.environ.get("HOME"),
        prefab_config_classpath_dir=".",
        prefab_envs=[],
        http_secure=None,
        on_no_default="RAISE",
        on_connection_failure="RETURN",
    ):
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

    def is_local_only(self):
        return self.prefab_datasources == "LOCAL_ONLY"

    def __set_url_for_api_cdn(self):
        if self.prefab_datasources == "LOCAL_ONLY":
            self.url_for_api_cdn = None
        else:
            cdn_url_from_env = os.environ.get("PREFAB_CDN_URL")
            if cdn_url_from_env is not None:
                self.url_for_api_cdn = cdn_url_from_env
            else:
                self.url_for_api_cdn = (
                    self.prefab_api_url.replace(".", "-") + ".global.ssl.fastly.net"
                )

    def __validate_datasource(datasource):
        if os.getenv("PREFAB_DATASOURCES") == "LOCAL_ONLY":
            default = "LOCAL_ONLY"
        else:
            default = "ALL"

        if datasource in ["LOCAL_ONLY", "ALL"]:
            return datasource
        else:
            return default

    def __set_api_key(self, api_key):
        if self.prefab_datasources == "LOCAL_ONLY":
            self.api_key = None
            return

        if api_key is None:
            raise MissingApiKeyException()
        api_key = str(api_key)
        if "-" not in api_key:
            raise InvalidApiKeyException(api_key)
        self.api_key = api_key

    def __set_api_url(self, api_url):
        if self.prefab_datasources == "LOCAL_ONLY":
            self.prefab_api_url = None
            return

        api_url = str(api_url)
        parsed_url = urlparse(api_url)
        if parsed_url.scheme in ["http", "https"]:
            self.prefab_api_url = api_url.rstrip("/")
        else:
            raise InvalidApiUrlException(api_url)

    def __set_grpc_url(self, grpc_url):
        if self.prefab_datasources == "LOCAL_ONLY":
            self.prefab_grpc_url = None
            return

        grpc_url = str(grpc_url)
        if grpc_url.startswith("grpc."):
            self.prefab_grpc_url = grpc_url
        else:
            raise InvalidGrpcUrlException(grpc_url)

    def __construct_prefab_envs(envs_from_input):
        all_envs = Options.__parse_envs(envs_from_input) + Options.__parse_envs(
            os.environ.get("PREFAB_ENVS")
        )
        all_envs.sort()
        return all_envs

    def __parse_envs(envs):
        if isinstance(envs, list):
            return envs
        if isinstance(envs, str):
            return [env.strip() for env in envs.split(",")]
        return []

    def __set_on_no_default(self, input):
        if input in ["RAISE", "RETURN_NONE"]:
            self.on_no_default = input
        else:
            self.on_no_default = "RAISE"

    def __set_on_connection_failure(self, input):
        if input in ["RETURN", "RAISE"]:
            self.on_connection_failure = input
        else:
            self.on_connection_failure = "RETURN"

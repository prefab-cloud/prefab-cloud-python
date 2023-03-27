import os
from urllib.parse import urlparse


class MissingApiKeyException(Exception):
    """Raised when no API key is found"""

    def __init__(self):
        super().__init__("No API key found")


class InvalidApiKeyException(Exception):
    """Raised when an invalid API key is provided"""

    def __init__(self, api_key):
        super().__init__("Invalid API key: %s" % api_key)


class InvalidApiUrlException(Exception):
    """Raised when an invalid API URL is given"""

    def __init__(self, url):
        super().__init__("Invalid API URL found: %s" % url)


class InvalidGrpcUrlException(Exception):
    """Raised when an invalid gRPC URL is given"""

    def __init__(self, url):
        super().__init__("Invalid gRPC URL found: %s" % url)


class Options:
    """Options used to configure a prefab_cloud_python.Client

    :param api_key: your prefab.cloud SDK API key
    :param prefab_api_url: the API endpoint your API key has been created for
        (e.g. `https://api.prefab.cloud`)
    :param prefab_grpc_url: the gRPC endpoint (including port) you wish to
        connect to (e.g. `grpc.prefab.cloud:443`)
    :param prefab_datasources: one of `'ALL'` or `'LOCAL_ONLY'`, determines,
        respectively whether to fetch data from remote sources or use only
        local data
    :param log_prefix: a prefix that will be attached to any logging done via
        a `Client` initialized with these options
    :param namespace: an optional namespace to define your client's scope when
        looking up config
    :param connection_timeout_seconds: the number of seconds to wait for the
        CDN and gRPC clients before timing out
    :param prefab_config_override_dir: the directory from which to load local
        override data. This data will overwrite data pulled from remote sources
    :param prefab_config_classpath_dir: the directory from which to load
        locally defined configuration. This data will be overwritten by
        data pulled from remote sources.
    :param prefab_envs: one or more environment names from which to load local
        configuration and overrides.
    :param on_no_default: one of `'RAISE'` (default) or `'RETURN_NONE'`.
        Determines whether a remote query for data that returns no value and
        has no default defined will raise an error (default) or return `None`.
    :param on_connection_failure: one of `'RETURN'` (default) or `'RAISE'`.
        Determines what should happen if the client fails to connect to
        any remote datasources while not running in local-only mode.

    ## API key and endpoints

    Your API key and endpoints can be defined inline when initializing your `Prefab.Options` struct, or in your
    application config. We recommend setting these values as environment variables and querying them from your
    `config/*.exs` files, i.e.

      config :prefab,
        api_key: System.get_env("PREFAB_API_KEY"),
        api_url: System.get_env("PREFAB_API_URL", "https://api.prefab.cloud"),
        grpc_url: System.get_env("PREFAB_GRPC_URL", "grpc.prefab.cloud:443")

    Your API key is expected to be a non-empty string, and to contain at least one (1) hyphen. If the first condition is not met,
    `Prefab.Options.new/1` will raise a `Prefab.Errors.MissingApiKeyError`, and if the second is not met, it will raise a `Prefab.Errors.InvalidApiKeyError`.

    If your options are configured for [local-only mode](#module-local-only-mode), these errors will be skipped, and the API key will be set to `nil`.

    ## Timeouts

    By default, the `Prefab.Client` will use a timeout of 10 seconds to connect
    to the CDN and gRPC remote clients, if not running in
    [local-only mode](#module-local-only-mode). If neither remote datasource can
    establish a connection, the client will log an appropriate error message and
    schedule itself to retry the connection.

    The length of the timeout can be set (in seconds), via the `connection_timeout_seconds`
    value when creating a new set of options.

    If you would prefer the client process to exit if no remote connection can be
    established, you can pass

      on_connection_failure: :raise

    to `Prefab.Options.new/1`, which will instruct the client process to
    exit if it fails to connect to either remote datasource within the allotted timeout window.

    ## Local-only mode

    There may be times when you want to create a Prefab client that does not connect to any remote data sources.

    You can do this in one of two ways:

    1. Pass `prefab_datasources: :local_only` explicitly into your options
    2. Set `export PREFAB_DATASOURCES=LOCAL_ONLY` in your environment

    If either of these two scenarios are true, Prefab will not attempt to connect to or pull data from the API or gRPC endpoints, but will
    rely on locally defined data (see below)

    **N.B.** Settings passed explicity into your options take precedence over the `$PREFAB_DATASOURCES` environment variable. That is,
    if your environment is set for local only, but you pass

      prefab_datasources: :all,

    into your options, your client *will* make remote calls.

    ## Namespace

    In the prefab.cloud UI, it is possible to scope a particular value for a key to a specific namespace. By providing a
    namespace to your client's options, the client will prefer to return values for keys that are defined for the given
    namespace, falling back to a less-specific namespace (all the way up to no namespace at all) until it finds a defined
    value. See [Prefab.Cloud | Docs | Explanations | Namespaces](https://docs.prefab.cloud/docs/explanations/namespaces)
    for a more complete discussion of how namespaces work in Prefab.

    ## Local config and overrides

    In addition to data pulled from the prefab.cloud API, it is possible to define configuration and feature flag data locally
    to be loaded by your `Prefab.Client`. You may wish to do this if you are running in `:local_only` mode but wish to still have
    data loaded in your environment, or are experimenting with configuration you do not wish to update in your live remote config.

    Prefab uses the `prefab_config_classpath_dir`, `prefab_config_override_dir`, and `prefab_envs` options to discover and load
    this local data. Data is loaded in the following order

    1. config defined under the `classpath_dir`
    2. config from the remote API (unless running in `:local_only` mode)
    3. overrides defined under the `override_dir`

    #### `prefab_envs`

    This value defines which local configuration and override files will be loaded by the client.

    This can be provided as a single value

      prefab_envs: "unit_tests"

    or a list

      prefab_envs: ["unit_tests", "feature_flags"]

    In addition to any environment names passed directly into `Prefab.Options.new/1`, the value of
    `$PREFAB_ENVS` (a single value or comma-separated list) will be parsed and appended to the end
    of the list given in the options.

    #### `prefab_config_classpath_dir`

    Prefab searches for YAML files located in this directory that match the naming schema `.prefab.ENV.config.{yml,yaml}`, where `ENV`
    is "default", or one of the environment names defined by the `prefab_envs` option.

    The "default" file, if found, is read first, and any files matching the `prefab_envs` are read and loaded in the order they are given
    in that option value.

    If not defined, this option will be set to `"."`

    #### `prefab_config_override_dir`

    Prefab searches for override YAML files located in this directory that match the naming schema `.prefab.ENV.config.{yml,yaml}`, where `ENV`
    is "overrides", or one of the environment names defined by the `prefab_envs` option.

    The "overrides" file, if found, is read first, and any files matching the `prefab_envs` are read and loaded in the order they are given
    in that option value.

    If not defined, this option will be set to your `$HOME` directory.
    """

    def __init__(
        self,
        api_key=None,
        prefab_api_url=None,
        prefab_grpc_url=None,
        prefab_datasources=None,
        logdev='STDIO',
        log_prefix=None,
        namespace='',
        connection_timeout_seconds=10,
        prefab_config_override_dir=os.environ.get("HOME"),
        prefab_config_classpath_dir=".",
        prefab_envs=[],
        http_secure=None,
        on_no_default='RAISE',
        on_connection_failure='RETURN',
    ):
        self.prefab_datasources = Options.__validate_datasource(
            prefab_datasources)
        self.__set_api_key(api_key or os.environ.get("PREFAB_API_KEY"))
        self.__set_api_url(prefab_api_url or os.environ.get(
            "PREFAB_API_URL") or "https://api.prefab.cloud")
        self.__set_grpc_url(prefab_grpc_url or os.getenv(
            "PREFAB_GRPC_URL") or "grpc.prefab.cloud:443")
        self.logdev = logdev
        self.log_prefix = log_prefix
        self.namespace = namespace
        self.connection_timeout_seconds = connection_timeout_seconds
        self.prefab_config_override_dir = prefab_config_override_dir
        self.prefab_config_classpath_dir = prefab_config_classpath_dir
        self.http_secure = http_secure or os.environ.get(
            "PREFAB_CLOUD_HTTP") != "true"
        self.prefab_envs = Options.__construct_prefab_envs(prefab_envs)
        self.stats = None
        self.shared_cache = None
        self.__set_url_for_api_cdn()
        self.__set_on_no_default(on_no_default)
        self.__set_on_connection_failure(on_connection_failure)

    def is_local_only(self):
        return self.prefab_datasources == 'LOCAL_ONLY'

    def __set_url_for_api_cdn(self):
        if self.prefab_datasources == "LOCAL_ONLY":
            self.url_for_api_cdn = None
        else:
            cdn_url_from_env = os.environ.get("PREFAB_CDN_URL")
            if cdn_url_from_env is not None:

                self.url_for_api_cdn = cdn_url_from_env
            else:
                self.url_for_api_cdn = self.prefab_api_url.replace(
                    ".", "-") + ".global.ssl.fastly.net"

    def __validate_datasource(datasource):
        if os.getenv("PREFAB_DATASOURCES") == 'LOCAL_ONLY':
            default = 'LOCAL_ONLY'
        else:
            default = 'ALL'

        if datasource in ['LOCAL_ONLY', 'ALL']:
            return datasource
        else:
            return default

    def __set_api_key(self, api_key):
        if self.prefab_datasources == 'LOCAL_ONLY':
            self.api_key = None
            return

        if api_key is None:
            raise MissingApiKeyException()
        api_key = str(api_key)
        if "-" not in api_key:
            raise InvalidApiKeyException(api_key)
        self.api_key = api_key

    def __set_api_url(self, api_url):
        if self.prefab_datasources == 'LOCAL_ONLY':
            self.prefab_api_url = None
            return

        api_url = str(api_url)
        parsed_url = urlparse(api_url)
        if parsed_url.scheme in ["http", "https"]:
            self.prefab_api_url = api_url.rstrip('/')
        else:
            raise InvalidApiUrlException(api_url)

    def __set_grpc_url(self, grpc_url):
        if self.prefab_datasources == 'LOCAL_ONLY':
            self.prefab_grpc_url = None
            return

        grpc_url = str(grpc_url)
        if grpc_url.startswith("grpc."):
            self.prefab_grpc_url = grpc_url
        else:
            raise InvalidGrpcUrlException(grpc_url)

    def __construct_prefab_envs(envs_from_input):
        all_envs = Options.__parse_envs(
            envs_from_input) + Options.__parse_envs(os.environ.get("PREFAB_ENVS"))
        all_envs.sort()
        return all_envs

    def __parse_envs(envs):
        if isinstance(envs, list):
            return envs
        if isinstance(envs, str):
            return [env.strip() for env in envs.split(",")]
        return []

    def __set_on_no_default(self, input):
        if input in ['RAISE', 'RETURN_NONE']:
            self.on_no_default = input
        else:
            self.on_no_default = 'RAISE'

    def __set_on_connection_failure(self, input):
        if input in ['RETURN', 'RAISE']:
            self.on_connection_failure = input
        else:
            self.on_connection_failure = 'RETURN'

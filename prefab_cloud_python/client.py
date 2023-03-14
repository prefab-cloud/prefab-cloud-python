import functools
from .config_client import ConfigClient
from .feature_flag_client import FeatureFlagClient
import prefab_pb2 as Prefab
from .logger_client import LoggerClient


class Client:
    max_sleep_sec = 10
    base_sleep_sec = 0.5
    no_default_provided = 'NO_DEFAULT_PROVIDED'

    def __init__(self, options):
        self.options = options
        self.namespace = options.namespace
        self.api_url = options.prefab_api_url
        self.grpc_url = options.prefab_grpc_url
        if options.is_local_only():
            self.logger().info("Prefab running in local-only mode")
        else:
            self.logger().info("Prefab connecting to %s and %s, secure %s" %
                               (options.prefab_api_url, options.prefab_grpc_url, options.http_secure))

    def get(self, key, default="NO_DEFAULT_PROVIDED", lookup_key=None, properties={}):
        if self.is_ff(key):
            if default == "NO_DEFAULT_PROVIDED":
                default = None
            return self.feature_flag_client().get(key, lookup_key=lookup_key, attributes=properties, default=default)
        else:
            return self.config_client().get(key, default=default, properties=properties, lookup_key=lookup_key)

    def enabled(self, feature_name, lookup_key=None, attributes={}):
        return self.feature_flag_client().feature_is_on_for(feature_name, lookup_key, attributes)

    def is_ff(self, key):
        raw = self.config_client().config_resolver.raw(key)
        if raw is not None and raw.config_type == Prefab.ConfigType.Value("FEATURE_FLAG"):
            return True
        return False

    @functools.cache
    def config_client(self):
        client = ConfigClient(self, timeout=5.0)
        self.logger().set_config_client(client)
        return client

    @functools.cache
    def feature_flag_client(self):
        return FeatureFlagClient(self)

    @functools.cache
    def logger(self):
        return LoggerClient()

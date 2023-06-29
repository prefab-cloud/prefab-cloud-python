import functools
import logging

from .context import Context
from .config_client import ConfigClient
from .feature_flag_client import FeatureFlagClient
from .context_shape_aggregator import ContextShapeAggregator
import base64
import prefab_pb2 as Prefab
import uuid
import requests

logger = logging.getLogger()


class Client:
    max_sleep_sec = 10
    base_sleep_sec = 0.5
    no_default_provided = "NO_DEFAULT_PROVIDED"

    def __init__(self, options):
        self.options = options
        self.instance_hash = str(uuid.uuid4())

        self.context_shape_aggregator = ContextShapeAggregator(
            self, self.options.collect_max_shapes, self.options.collect_sync_interval
        )

        if not options.is_local_only():
            self.context_shape_aggregator.start_periodic_sync()

        self.namespace = options.namespace
        self.api_url = options.prefab_api_url
        self.grpc_url = options.prefab_grpc_url
        self.session = requests.Session()
        if options.is_local_only():
            logger.info("Prefab running in local-only mode")
        else:
            logger.info(
                "Prefab connecting to %s and %s, secure %s"
                % (
                    options.prefab_api_url,
                    options.prefab_grpc_url,
                    options.http_secure,
                ),
            )

        self.context().clear()
        self.config_client()

    def get(self, key, default="NO_DEFAULT_PROVIDED", context="NO_CONTEXT_PROVIDED"):
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

    def enabled(self, feature_name, context="NO_CONTEXT_PROVIDED"):
        return self.feature_flag_client().feature_is_on_for(
            feature_name, context=self.resolve_context_argument(context)
        )

    def is_ff(self, key):
        raw = self.config_client().config_resolver.raw(key)
        if raw is not None and raw.config_type == Prefab.ConfigType.Value(
            "FEATURE_FLAG"
        ):
            return True
        return False

    def resolve_context_argument(self, context):
        if context != "NO_CONTEXT_PROVIDED":
            return context
        return Context.get_current()

    def context(self):
        return Context.get_current()

    def scoped_context(context):
        return Context.scope(context)

    @functools.cache
    def config_client(self):
        client = ConfigClient(self, timeout=5.0)
        return client

    @functools.cache
    def feature_flag_client(self):
        return FeatureFlagClient(self)

    def post(self, path, body):
        auth = "%s:%s" % ("authuser", self.options.api_key)
        auth_token = base64.b64encode(auth.encode("utf-8")).decode("ascii")

        headers = {
            "Content-Type": "application/x-protobuf",
            "Accept": "application/x-protobuf",
            "Authorization": f"Basic {auth_token}",
        }

        endpoint = self.options.prefab_api_url.strip("/") + "/" + path.strip("/")
        self.session.post(endpoint, headers=headers, data=body.SerializeToString())

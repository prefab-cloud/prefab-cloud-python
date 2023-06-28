import structlog
import os
from ._processors import clean_event_dict, set_location, log_or_drop


def apply_structlog_config():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ],
                additional_ignores=["prefab_cloud_python.logger_client"],
            ),
            set_location,
            log_or_drop,
            clean_event_dict,
            structlog.dev.ConsoleRenderer(),
        ]
    )


class BootstrappingConfigClient:
    def get(self, _key, default=None, context=None):
        bootstrap_log_level = os.environ.get("PREFAB_LOG_CLIENT_BOOTSTRAP_LOG_LEVEL")
        if bootstrap_log_level is not None:
            return bootstrap_log_level.upper()
        return default


class LoggerClient:
    def __init__(self, log_prefix=None, log_boundary=None, log_path_aggregator=None):
        self.log_prefix = log_prefix
        self.log_boundary = log_boundary
        self.config_client = BootstrappingConfigClient()
        self.log_path_aggregator = log_path_aggregator

    def debug(self, msg):
        self.configured_logger().debug(msg)

    def info(self, msg):
        self.configured_logger().info(msg)

    def warn(self, msg):
        self.configured_logger().warn(msg)

    def error(self, msg):
        self.configured_logger().error(msg)

    def critical(self, msg):
        self.configured_logger().critical(msg)

    def log_internal(self, level, msg, path=None):
        internal_logger = self.configured_logger().bind(
            skip_aggregator=True, internal_path=path
        )
        getattr(internal_logger, level)(msg)

    def set_config_client(self, config_client):
        self.config_client = config_client

    def add_config_client(self, _, __, event_dict):
        event_dict["config_client"] = self.config_client
        return event_dict

    def configured_logger(self):
        if not structlog.is_configured():
            apply_structlog_config()

        return structlog.get_logger().bind(
            config_client=self.config_client,
            log_prefix=self.log_prefix,
            log_boundary=self.log_boundary,
            log_path_aggregator=self.log_path_aggregator,
            skip_aggregator=False,
        )

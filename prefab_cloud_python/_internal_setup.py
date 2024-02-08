import structlog

from prefab_cloud_python import LoggerFilter


def default_structlog_setup(colors=True):
    logger_filter = LoggerFilter()
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.processors.add_log_level,
            logger_filter.processor,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(colors=colors),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),  # Use Python's logging factory
        wrapper_class=structlog.stdlib.BoundLogger,
    )

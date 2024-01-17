from .structlog_multi_processor import StructlogMultiProcessor
from ._structlog_processors import clean_event_dict, set_location, log_or_drop
import structlog
from .constants import STRUCTLOG_CALLSITE_IGNORES


def create_prefab_structlog_processor():
    return StructlogMultiProcessor([set_location, log_or_drop, clean_event_dict])


def default_structlog_setup(colors=True):
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
                additional_ignores=STRUCTLOG_CALLSITE_IGNORES,
            ),
            create_prefab_structlog_processor(),
            structlog.dev.ConsoleRenderer(colors=colors),
        ]
    )

import time
import prefab_cloud_python
import structlog
from prefab_cloud_python import Options, LoggerProcessor


class CustomLoggerNameProcessor(LoggerProcessor):
    def logger_name(self, logger, event_dict: dict) -> str:
        return event_dict.get("module")


###
# This example shows logger configuration and printing a config value in a loop
# to run set PREFAB_API_KEY
def main():
    # basic logging setup, for example only
    # in a real setup one would probably want to integrate stdlib logging into this configuration
    # includes the MODULE callsite parameter that the CustomLoggerNameProcessor will use as the logger name
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.MODULE,
                }
            ),
            CustomLoggerNameProcessor().processor,
            structlog.dev.ConsoleRenderer(pad_event=25),
        ]
    )

    logger = structlog.getLogger()
    options = Options()
    prefab_cloud_python.set_options(options)
    while True:
        time.sleep(1)
        logger.warning(
            f"value of `example-config` is {prefab_cloud_python.get_client().get('example-config', default='default value')}"
        )
        logger.error("ERROR message")
        logger.warning("WARN message")
        logger.info("INFO message")
        logger.debug("DEBUG message")


if __name__ == "__main__":
    main()

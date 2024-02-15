import logging
import sys
import time
import prefab_cloud_python
from prefab_cloud_python import Options, LoggerFilter

###
# This example shows logger configuration and printing a config value in a loop
# to run set PREFAB_API_KEY
def main():
    # basic logging setup
    root_logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(handler)

    def configure_logger():
        # add the prefab filter, lower the overall logging level to DEBUG so the filter can handle every log message
        handler.addFilter(LoggerFilter())
        logging.basicConfig(level=logging.DEBUG)
        logging.warning("Logger configured")

    logger = logging.getLogger("prefab.python.test.logger")
    options = Options(bootstrap_loglevel=logging.DEBUG, on_ready_callback=configure_logger)
    prefab_cloud_python.set_options(options)
    while True:
        time.sleep(1)
        logger.warning(
            f"value of `example-config` is {prefab_cloud_python.get_client().get('example-config', default='default value')}")
        logger.error("ERROR message")
        logger.warning("WARN message")
        logger.info("INFO message")
        logger.debug("DEBUG message")


if __name__ == "__main__":
    main()

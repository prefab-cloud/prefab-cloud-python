import prefab_pb2 as Prefab

import time
import timecop

from prefab_cloud_python.log_path_aggregator import LogPathAggregator
from prefab_cloud_python.logger_client import LoggerClient


class TestLogPathAggregator:
    def test_sync(self):
        with timecop.freeze(time.time()):
            logger_path_aggregator = LogPathAggregator(LoggerClient(), 120)

            for _ in range(2):
                logger_path_aggregator.push("path1", "INFO")
            for _ in range(3):
                logger_path_aggregator.push("path1", "ERROR")

            loggers = logger_path_aggregator.flush()
            assert loggers == Prefab.LoggersTelemetryEvent(
                loggers=[
                    Prefab.Logger(
                        logger_name="path1",
                        infos=2,
                        errors=3,
                    )
                ],
                start_at=round(time.time() * 1000),
                end_at=round(time.time() * 1000),
            )

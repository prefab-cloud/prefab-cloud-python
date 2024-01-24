import time
from collections import defaultdict
import prefab_pb2 as Prefab


class LogPathAggregator:
    def __init__(self, logger, max_paths):
        self.max_paths = max_paths
        self.start_at = time.time()
        self.paths = defaultdict(int)
        self.logger = logger

    def push(self, path, severity):
        if len(self.paths) >= self.max_paths:
            return

        self.paths[(path, severity)] += 1

    def flush(self):
        to_ship = self.paths.copy()
        self.paths = defaultdict(int)

        start_at_was = self.start_at
        self.start_at = time.time()

        self.logger.log_internal("debug", "Uploading stats for %s paths" % len(to_ship))

        aggregate = defaultdict(lambda: Prefab.Logger())

        for (path, severity), count in to_ship.items():
            if severity == "DEBUG":
                aggregate[path].debugs = count
            elif severity == "INFO":
                aggregate[path].infos = count
            elif severity == "WARN":
                aggregate[path].warns = count
            elif severity == "ERROR":
                aggregate[path].errors = count
            elif severity == "FATAL":
                aggregate[path].fatals = count
            aggregate[path].logger_name = path

        loggers = Prefab.LoggersTelemetryEvent(
            loggers=aggregate.values(),
            start_at=round(start_at_was * 1000),
            end_at=round(time.time() * 1000),
        )
        return loggers

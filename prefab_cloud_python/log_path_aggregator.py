import time
from collections import defaultdict
import prefab_pb2 as Prefab
import threading


class LogPathAggregator:
    def __init__(self, client, max_paths, sync_interval):
        self.client = client
        self.max_paths = max_paths
        self.sync_interval = sync_interval or 8

        self.start_at = time.time()
        self.paths = defaultdict(int)

    def push(self, path, severity):
        if len(self.paths) >= self.max_paths:
            return

        self.paths[(path, severity)] += 1

    def sync(self):
        if len(self.paths) > 0:
            self.client.logger.log_internal(
                "debug", "Syncing %s paths" % len(self.paths)
            )
            self.flush()

    def flush(self):
        to_ship = self.paths.copy()
        self.paths = defaultdict(int)

        start_at_was = self.start_at
        self.start_at = time.time()

        self.client.logger.log_internal(
            "debug", "Uploading stats for %s paths" % len(to_ship)
        )

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

        loggers = Prefab.Loggers(
            loggers=aggregate.values(),
            start_at=round(start_at_was * 1000),
            end_at=round(time.time() * 1000),
            instance_hash=self.client.instance_hash,
            namespace=self.client.namespace,
        )

        self.client.post("/api/v1/known-loggers", loggers)

    def start_periodic_sync(self):
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.sync_thread.start()

    def sync_loop(self):
        self.client.logger.log_internal(
            "debug",
            f"Initialized log path collection instance_hash={self.client.instance_hash} max_paths={self.max_paths}",
        )
        while True:
            time.sleep(self.sync_interval)
            self.sync()

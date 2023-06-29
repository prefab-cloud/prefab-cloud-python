import logging

from .context_shape import ContextShape
import prefab_pb2 as Prefab
import time
import threading


class ContextShapeAggregator:
    def __init__(self, client, max_shapes, sync_interval):
        self.logger = logging.getLogger()
        self.client = client
        self.max_shapes = max_shapes
        self.sync_interval = sync_interval or 0

        self.start_at = time.time()
        self.data = set()

    def push(self, context):
        if len(self.data) >= self.max_shapes:
            return

        for name, named_context in context.contexts.items():
            for key, value in named_context.data.items():
                self.data.add((name, key, ContextShape.field_type_number(value)))

    def prepare_data(self):
        to_ship = self.data.copy()
        self.data = set()

        ret = {}
        for name, key, value in to_ship:
            ret.setdefault(name, {})
            ret[name][key] = value

        return ret

    def sync(self):
        if len(self.data) > 0:
            self.logger.debug("Syncing %s shapes" % len(self.data))
            self.flush()

    def flush(self):
        to_ship = self.prepare_data()

        self.logger.debug("Uploading stats for %s context shapes" % len(to_ship))

        shapes = []
        for name in sorted(to_ship.keys()):
            shapes.append(Prefab.ContextShape(name=name, field_types=to_ship[name]))

        data_to_post = Prefab.ContextShapes(shapes=shapes)

        self.client.post("/api/v1/context-shapes", data_to_post)

    def start_periodic_sync(self):
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.sync_thread.start()

    def sync_loop(self):
        self.logger.debug(
            f"Initialized context shape collection instance_hash={self.client.instance_hash} max_shapes={self.max_shapes}"
        )
        while True:
            time.sleep(self.sync_interval)
            self.sync()

from .context import Context
from .read_write_lock import ReadWriteLock
from .criteria_evaluator import CriteriaEvaluator


class ConfigResolver:
    def __init__(self, base_client, config_loader):
        self.lock = ReadWriteLock()
        self.base_client = base_client
        self.config_loader = config_loader
        self.project_env_id = 0
        self.make_local()

    def get(self, key, lookup_key, properties={}, context=Context.get_current()):
        self.lock.acquire_read()
        raw_config = self.raw(key)
        self.lock.release_read()

        if raw_config is None:
            return None
        return self.evaluate(raw_config, lookup_key, properties, context=context)

    def raw(self, key):
        via_key = self.local_store.get(key)
        if via_key is not None:
            return via_key["config"]
        return None

    def evaluate(
        self, config, lookup_key, properties={}, context=Context.get_current()
    ):
        return CriteriaEvaluator(
            config,
            project_env_id=self.project_env_id,
            resolver=self,
            base_client=self.base_client,
        ).evaluate(self.evaluation_context(context))

    def evaluation_context(self, context):
        if isinstance(context, Context):
            return context
        else:
            return Context.merge_with_current(context)

    def update(self):
        self.make_local()

    def make_local(self):
        self.lock.acquire_write()
        self.local_store = self.config_loader.calc_config()
        self.lock.release_write()

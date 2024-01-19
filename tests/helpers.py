from prefab_cloud_python import Context
from prefab_cloud_python.config_resolver import CriteriaEvaluator


class MockResolver:
    def __init__(self, config):
        self.config = config

    def raw(self, key):
        self.config.get(key)

    def get(self, key, context=Context({})):
        return CriteriaEvaluator(
            self.config.get(key), project_env_id=None, resolver=None, base_client=None
        ).evaluate(context)


class EmptyResolver:
    def __init__(self):
        pass

    def raw(self, key):
        return None

    def get(self, key, context=Context({})):
        return None

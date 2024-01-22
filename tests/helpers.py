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


def sort_proto_evaluation_summaries(summaries):
    return sorted(summaries, key=lambda obj: (obj.key, obj.type))


def sort_proto_evaluation_counters(counters):
    return sorted(
        counters,
        key=lambda obj: (
            obj.config_id,
            obj.selected_index,
            obj.config_row_index,
            obj.conditional_value_index,
            obj.weighted_value_index,
            obj.selected_value.SerializeToString(),
        ),
    )

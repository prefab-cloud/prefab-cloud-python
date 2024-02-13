import pytest

from prefab_cloud_python import Options
from prefab_cloud_python.config_resolver import ConfigResolver
from prefab_cloud_python.context import Context


class FakeConfigLoader:
    def __init__(self):
        pass

    def calc_config(self):
        return {}


class FakeClient:
    def __init__(self, options=None):
        self.options = options


class ConfigResolverFactoryFixture:
    def __init__(self):
        self.client = None

    def create(self, global_context={}, default_context={}) -> ConfigResolver:
        options = Options(
            global_context=global_context, prefab_datasources="LOCAL_ONLY"
        )
        config_resolver = ConfigResolver(
            FakeClient(options=options), FakeConfigLoader()
        )
        config_resolver.default_context = default_context
        return config_resolver


@pytest.fixture
def config_resolver_factory():
    return ConfigResolverFactoryFixture()


class ContextMergingTests:
    def test_empty_contexts(self, config_resolver_factory):
        config_resolver = config_resolver_factory.create()
        assert config_resolver.evaluation_context(None).to_dict() == {}

    def test_global_context(self, config_resolver_factory):
        global_context_dict = {
            "flavor": {"key": "tart"},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
        }
        config_resolver = config_resolver_factory.create(
            global_context=global_context_dict
        )
        assert config_resolver.evaluation_context(None).to_dict() == global_context_dict

    def test_global_plus_default_context(self, config_resolver_factory):
        global_context_dict = {
            "flavor": {"key": "tart"},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
        }
        default_context_dict = {"flavor": {"key": "sweet"}, "color": {"key": "red"}}
        config_resolver = config_resolver_factory.create(
            global_context=global_context_dict, default_context=default_context_dict
        )
        assert config_resolver.evaluation_context(None).to_dict() == {
            "flavor": {"key": "sweet"},
            "color": {"key": "red"},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
        }

    def test_global_plus_default_plus_implicit_context_sources(
        self, config_resolver_factory
    ):
        global_context_dict = {
            "flavor": {"key": "tart", "scale": 5},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
        }
        default_context_dict = {
            "flavor": {"key": "sweet", "scale": 2},
            "color": {"key": "red"},
        }
        Context.set_current(
            {"flavor": {"key": "sour", "scale": 10}, "gmo_status": {"key": "yes"}}
        )

        config_resolver = config_resolver_factory.create(
            global_context=global_context_dict, default_context=default_context_dict
        )
        assert config_resolver.evaluation_context(None).to_dict() == {
            "flavor": {"key": "sour", "scale": 10},
            "color": {"key": "red"},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
            "gmo_status": {"key": "yes"},
        }

    def test_all_context_sources(self, config_resolver_factory):
        global_context_dict = {
            "flavor": {"key": "tart", "scale": 5},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
        }
        default_context_dict = {
            "flavor": {"key": "sweet", "scale": 2},
            "color": {"key": "red"},
        }
        Context.set_current(
            {"flavor": {"key": "sour", "scale": 10}, "gmo_status": {"key": "yes"}}
        )
        passed_context = {"flavor": {"key": "spicy", "scale": 9}}

        config_resolver = config_resolver_factory.create(
            global_context=global_context_dict, default_context=default_context_dict
        )
        assert config_resolver.evaluation_context(passed_context).to_dict() == {
            "flavor": {"key": "spicy", "scale": 9},
            "color": {"key": "red"},
            "texture": {"key": "crunchy"},
            "size": {"key": "medium"},
            "gmo_status": {"key": "yes"},
        }

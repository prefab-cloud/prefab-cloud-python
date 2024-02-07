from prefab_cloud_python import Options, Client
from prefab_cloud_python.config_client import MissingDefaultException
import prefab_pb2 as Prefab
import pytest
import os

from contextlib import contextmanager


@contextmanager
def extended_env(new_env_vars):
    old_env = os.environ.copy()
    os.environ.update(new_env_vars)
    yield
    os.environ.clear()
    os.environ.update(old_env)


class TestConfigClient:
    def test_get(self):
        config_client = self.build_config_client()

        assert config_client.get("sample") == "test sample value"
        assert config_client.get("sample_int") == 123
        assert config_client.get("sample_double") == 12.12
        assert config_client.get("sample_bool")
        assert config_client.get("log-level.app") == Prefab.LogLevel.Value("ERROR")

    def test_get_with_default(self):
        config_client = self.build_config_client()

        assert config_client.get("bad key", "default value") == "default value"

    def test_get_without_default_raises(self):
        config_client = self.build_config_client()

        with pytest.raises(MissingDefaultException) as exception:
            config_client.get("bad key")

        assert "No value found for key 'bad key' and no default was provided." in str(
            exception.value
        )

    def test_get_without_default_returns_none_if_configured(self):
        config_client = self.build_config_client("RETURN_NONE")
        assert config_client.get("bad key") is None

    def test_caching(self):
        config_client = self.build_config_client()
        cached_config = Prefab.Configs(
            configs=[
                Prefab.Config(
                    key="test",
                    id=1,
                    rows=[
                        Prefab.ConfigRow(
                            values=[
                                Prefab.ConditionalValue(
                                    value=Prefab.ConfigValue(string="test value")
                                )
                            ]
                        )
                    ],
                )
            ],
            config_service_pointer=Prefab.ConfigServicePointer(
                project_id=3, project_env_id=5
            ),
        )
        config_client.cache_configs(cached_config)

        config_client.load_cache()
        assert config_client.get("test") == "test value"

    def test_cache_path(self):
        options = Options(api_key="123-API-KEY-SDK", x_use_local_cache=True, collect_sync_interval=None)
        client = Client(options)
        assert (
            client.config_client().cache_path
            == f"{os.environ['HOME']}/.cache/prefab.cache.123.json"
        )

    def test_cache_path_local_only(self):
        config_client = self.build_config_client()
        assert (
            config_client.cache_path
            == f"{os.environ['HOME']}/.cache/prefab.cache.local.json"
        )

    def test_cache_path_respects_xdg(self):
        with extended_env({"XDG_CACHE_HOME": "/tmp"}):
            config_client = self.build_config_client()
            assert config_client.cache_path == "/tmp/prefab.cache.local.json"

    @staticmethod
    def build_config_client(on_no_default="RAISE"):
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs="unit_tests",
            prefab_datasources="LOCAL_ONLY",
            x_use_local_cache=True,
            on_no_default=on_no_default,
            collect_sync_interval=None
        )
        client = Client(options)
        return client.config_client()

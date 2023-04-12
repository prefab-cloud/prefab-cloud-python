from prefab_cloud_python import Options, Client
from prefab_cloud_python.config_client import MissingDefaultException
import prefab_pb2 as Prefab
import pytest


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

    @staticmethod
    def build_config_client(on_no_default="RAISE"):
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs="unit_tests",
            prefab_datasources="LOCAL_ONLY",
            on_no_default=on_no_default,
        )
        client = Client(options)
        return client.config_client()

from prefab_cloud_python import Client, Options, LoggerFilter
import pytest
import os
import prefab_pb2 as Prefab


@pytest.fixture
def config_client():
    options = Options(
        prefab_config_classpath_dir="tests",
        prefab_envs=["unit_tests"],
        prefab_datasources="LOCAL_ONLY",
    )
    client = Client(options)
    return client.config_client()


class TestLoggerFilter:
    def test_get_path(self, config_client):
        filter = LoggerFilter(config_client)
        assert (
            filter.get_path(
                "/Users/user/.asdf/installs/python/3.11.2/lib/python3.11/site-packages/my_lib.py",
                "my_func",
            )
            == "my_lib.my_func"
        )

    def test_get_path_with_prefix(self, config_client):
        filter = LoggerFilter(config_client, prefix="my.prefix")
        assert (
            filter.get_path(
                "/Users/user/.asdf/installs/python/3.11.2/lib/python3.11/site-packages/my_lib.py",
                "my_func",
            )
            == "my.prefix.my_lib.my_func"
        )

    def test_get_path_without_site_packages(self, config_client):
        filter = LoggerFilter(config_client)
        assert (
            filter.get_path(
                os.environ["HOME"] + "/Code/my_app/my_app/my_lib.py", "my_func"
            )
            == "code.my_app.my_app.my_lib.my_func"
        )

    def test_get_path_without_site_packages_and_explicit_boundary(self, config_client):
        filter = LoggerFilter(config_client, log_boundary="/Users/user/Code/my_app")
        assert (
            filter.get_path("/Users/user/Code/my_app/my_app/my_lib.py", "my_func")
            == "my_app.my_lib.my_func"
        )

    def test_get_severity(self, config_client):
        filter = LoggerFilter(config_client)

        assert filter.get_severity("") == Prefab.LogLevel.Value("WARN")
        assert filter.get_severity("app") == Prefab.LogLevel.Value("ERROR")
        assert filter.get_severity("app.controller") == Prefab.LogLevel.Value("ERROR")
        assert filter.get_severity("app.controller.hello") == Prefab.LogLevel.Value(
            "WARN"
        )
        assert filter.get_severity(
            "app.controller.hello.index"
        ) == Prefab.LogLevel.Value("INFO")
        assert filter.get_severity(
            "app.controller.hello.edit"
        ) == Prefab.LogLevel.Value("WARN")

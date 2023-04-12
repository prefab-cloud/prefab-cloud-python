from prefab_cloud_python._processors import get_path, get_severity
from prefab_cloud_python import Options, Client
import prefab_pb2 as Prefab
import pytest
import re


@pytest.fixture
def client():
    options = Options(
        prefab_config_classpath_dir="tests",
        prefab_envs=["unit_tests"],
        prefab_datasources="LOCAL_ONLY",
    )
    return Client(options)


class TestLoggerClient:
    def test_get_path(self):
        assert (
            get_path(
                "/Users/mikowitz/.asdf/installs/python/3.10.7/lib/python3.10/site-packages/my_lib.py",
                "my_func",
            )
            == "my_lib.my_func"
        )
        assert (
            get_path(
                "/Users/mikowitz/.asdf/installs/python/3.10.7/lib/python3.10/site-packages/my_lib.py",
                "my_func",
                "my.prefix",
            )
            == "my.prefix.my_lib.my_func"
        )
        assert (
            get_path("/Users/mikowitz/Code/my_app/my_app/my_lib.py", "my_func")
            == "my_app.my_app.my_lib.my_func"
        )

    def test_get_severity(self, client):
        config_client = client.config_client()

        assert get_severity("", config_client) == Prefab.LogLevel.Value("WARN")
        assert get_severity("app", config_client) == Prefab.LogLevel.Value("ERROR")
        assert get_severity("app.controller", config_client) == Prefab.LogLevel.Value(
            "ERROR"
        )
        assert get_severity(
            "app.controller.hello", config_client
        ) == Prefab.LogLevel.Value("WARN")
        assert get_severity(
            "app.controller.hello.index", config_client
        ) == Prefab.LogLevel.Value("INFO")
        assert get_severity(
            "app.controller.hello.edit", config_client
        ) == Prefab.LogLevel.Value("WARN")

    def test_capture_output(self, client, capsys):
        logger = client.logger()

        logger.warn("ok")

        captured = capsys.readouterr()
        log_pattern = re.compile(".*warning.*ok.*")
        location_pattern = re.compile(
            ".*location.*=.*prefab_cloud_python.tests.test_logger_client.test_capture_output"
        )
        assert log_pattern.match(captured.out)
        assert location_pattern.match(captured.out)

    def test_no_output_for_lower_log_level(self, client, capsys):
        logger = client.logger()

        logger.debug("ok")

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_log_prefix_from_client(self, capsys):
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs=["unit_tests"],
            prefab_datasources="LOCAL_ONLY",
            log_prefix="my.prefix",
        )
        client = Client(options)

        logger = client.logger()

        logger.warn("ok")

        captured = capsys.readouterr()
        log_pattern = re.compile(".*warning.*ok.*")
        location_pattern = re.compile(
            ".*location.*=.*my.prefix.prefab_cloud_python.tests.test_logger_client.test_log_prefix_from_client"
        )
        assert log_pattern.match(captured.out)
        assert location_pattern.match(captured.out)

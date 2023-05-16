from prefab_cloud_python._processors import get_path, get_severity
from prefab_cloud_python import Options, Client
import prefab_pb2 as Prefab
import pytest
import re
import os


@pytest.fixture
def client():
    options = Options(
        prefab_config_classpath_dir="tests",
        prefab_envs=["unit_tests"],
        prefab_datasources="LOCAL_ONLY",
    )
    return Client(options)


def assert_logged(cap, level, msg, path, should_log=True):
    pattern = re.compile(f".*{level}.*{msg}.*location.*{path}.*")
    stdout, stderr = cap.readouterr()
    if should_log:
        assert pattern.match(stdout)
    else:
        assert not pattern.match(stdout)


project_env_id = 1
test_env_id = 2
default_value = "FATAL"
default_env_value = "INFO"
desired_env_value = "DEBUG"
wrong_env_value = "ERROR"
default_row = Prefab.ConfigRow(
    values=[Prefab.ConditionalValue(value=Prefab.ConfigValue(log_level=default_value))]
)


class TestLoggerClient:
    def test_get_path(self):
        assert (
            get_path(
                "/Users/user/.asdf/installs/python/3.10.7/lib/python3.10/site-packages/my_lib.py",
                "my_func",
            )
            == "my_lib.my_func"
        )

    def test_get_path_with_prefix(self):
        assert (
            get_path(
                "/Users/user/.asdf/installs/python/3.10.7/lib/python3.10/site-packages/my_lib.py",
                "my_func",
                "my.prefix",
            )
            == "my.prefix.my_lib.my_func"
        )

    def test_get_path_without_site_packages(self):
        assert (
            get_path(os.environ["HOME"] + "/Code/my_app/my_app/my_lib.py", "my_func")
            == "code.my_app.my_app.my_lib.my_func"
        )

    def test_get_path_without_site_packages_and_explicit_boundary(self):
        assert (
            get_path(
                "/Users/user/Code/my_app/my_app/my_lib.py",
                "my_func",
                log_boundary="/Users/user/Code/my_app",
            )
            == "my_app.my_lib.my_func"
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
            ".*location.*=.*my.prefix.*.prefab_cloud_python.tests.test_logger_client.test_log_prefix_from_client"
        )
        assert log_pattern.match(captured.out)
        assert location_pattern.match(captured.out)

    def test_log_eval_rules_on_top_level_key(self, client, capsys):
        config = Prefab.Config(
            key="log-level",
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=test_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(
                                            values=["hotmail.com", "gmail.com"]
                                        )
                                    ),
                                    property_name="user.email_suffix",
                                )
                            ],
                            value=Prefab.ConfigValue(log_level=wrong_env_value),
                        )
                    ],
                ),
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(
                                            values=["hotmail.com", "gmail.com"]
                                        )
                                    ),
                                    property_name="user.email_suffix",
                                )
                            ],
                            value=Prefab.ConfigValue(log_level=desired_env_value),
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(log_level=default_env_value)
                        ),
                    ],
                ),
            ],
        )

        client.config_client().config_resolver.local_store[config.key] = {
            "config": config
        }
        client.config_client().config_resolver.project_env_id = project_env_id

        logger = client.logger()

        with Client.scoped_context({}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "debug", "Test debug", "tests.test_logger", should_log=False
            )

            logger.info("Test info")
            assert_logged(capsys, "info", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "error", "Test error", "tests.test_logger")

        with Client.scoped_context({"user": {"email_suffix": "yahoo.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "debug", "Test debug", "tests.test_logger", should_log=False
            )

            logger.info("Test info")
            assert_logged(capsys, "info", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "error", "Test error", "tests.test_logger")

        with Client.scoped_context({"user": {"email_suffix": "hotmail.com"}}):
            logger.debug("Test debug")
            assert_logged(capsys, "debug", "Test debug", "tests.test_logger")

            logger.info("Test info")
            assert_logged(capsys, "info", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "error", "Test error", "tests.test_logger")

    def test_log_eval_rules_on_key_path(self, capsys):
        config = Prefab.Config(
            key="log-level.my.own.prefix",
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=test_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(
                                            values=["hotmail.com", "gmail.com"]
                                        )
                                    ),
                                    property_name="user.email_suffix",
                                )
                            ],
                            value=Prefab.ConfigValue(log_level=wrong_env_value),
                        )
                    ],
                ),
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(
                                            values=["hotmail.com", "gmail.com"]
                                        )
                                    ),
                                    property_name="user.email_suffix",
                                )
                            ],
                            value=Prefab.ConfigValue(log_level=desired_env_value),
                        ),
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(
                                            values=["user:4567"]
                                        )
                                    ),
                                    property_name="user.tracking_id",
                                )
                            ],
                            value=Prefab.ConfigValue(log_level=desired_env_value),
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(log_level=default_env_value)
                        ),
                    ],
                ),
            ],
        )

        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs=["unit_tests"],
            prefab_datasources="LOCAL_ONLY",
            log_prefix="my.own.prefix",
        )
        client = Client(options)

        client.config_client().config_resolver.local_store[config.key] = {
            "config": config
        }
        client.config_client().config_resolver.project_env_id = project_env_id

        logger = client.logger()

        with Client.scoped_context({}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "debug",
                "Test debug",
                "my.own.prefix.*tests.test_logger",
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(
                capsys, "info", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "error", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"email_suffix": "yahoo.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "debug",
                "Test debug",
                "my.own.prefix.*tests.test_logger",
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(
                capsys, "info", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "error", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"email_suffix": "hotmail.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "debug", "Test debug", "my.own.prefix.*tests.test_logger"
            )

            logger.info("Test info")
            assert_logged(
                capsys, "info", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "error", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"tracking_id": "user:4567"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "debug", "Test debug", "my.own.prefix.*tests.test_logger"
            )

            logger.info("Test info")
            assert_logged(
                capsys, "info", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "error", "Test error", "my.own.prefix.*tests.test_logger"
            )

from prefab_cloud_python import Client, Options, LoggerFilter
import logging
import pytest
import os
import prefab_pb2 as Prefab
import re
import sys

project_env_id = 1
test_env_id = 2
default_value = "FATAL"
default_env_value = "INFO"
desired_env_value = "DEBUG"
wrong_env_value = "ERROR"
default_row = Prefab.ConfigRow(
    values=[Prefab.ConditionalValue(value=Prefab.ConfigValue(log_level=default_value))]
)


def assert_logged(cap, level, msg, path, should_log=True):
    pattern = re.compile(f".*{level}.*{path}.*{msg}.*")
    stdout, stderr = cap.readouterr()
    if should_log:
        assert pattern.match(stdout)
    else:
        assert not pattern.match(stdout)


@pytest.fixture
def config_client():
    options = Options(
        prefab_config_classpath_dir="tests",
        prefab_envs=["unit_tests"],
        prefab_datasources="LOCAL_ONLY",
        collect_sync_interval=None,
    )
    client = Client(options)
    return client.config_client()


def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)

    return (logger, ch)


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

    def test_capture_output(self, config_client, capsys):
        (logger, ch) = configure_logger()
        filter = LoggerFilter(config_client)
        ch.addFilter(filter)

        logger.warning("ok")

        captured = capsys.readouterr()
        log_pattern = re.compile(".*WARNING.*")
        location_pattern = re.compile(
            ".*prefab_cloud_python.tests.test_logger_filter.test_capture_output.*ok.*"
        )
        assert log_pattern.match(captured.out)
        assert location_pattern.match(captured.out)

    def test_no_output_for_lower_log_level(self, config_client, capsys):
        (logger, ch) = configure_logger()
        filter = LoggerFilter(config_client)
        ch.addFilter(filter)

        logger.debug("ok")

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_log_prefix_from_client(self, capsys):
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs=["unit_tests"],
            prefab_datasources="LOCAL_ONLY",
            log_prefix="my.prefix",
            collect_sync_interval=None,
        )
        client = Client(options)

        (logger, ch) = configure_logger()
        filter = LoggerFilter(client.config_client(), prefix=client.options.log_prefix)
        ch.addFilter(filter)

        logger.warning("ok")

        captured = capsys.readouterr()
        location_pattern = re.compile(
            ".*my.prefix.*.prefab_cloud_python.tests.test_logger_filter.test_log_prefix_from_client"
        )
        # assert log_pattern.match(captured.out)
        assert location_pattern.match(captured.out)

    def test_log_eval_rules_on_top_level_key(self, config_client, capsys):
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

        config_client.config_resolver.local_store[config.key] = {"config": config}
        config_client.config_resolver.project_env_id = project_env_id

        (logger, ch) = configure_logger()
        filter = LoggerFilter(config_client)
        ch.addFilter(filter)

        with Client.scoped_context({}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "DEBUG", "Test debug", "tests.test_logger", should_log=False
            )

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", "tests.test_logger")

        with Client.scoped_context({"user": {"email_suffix": "yahoo.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "DEBUG", "Test debug", "tests.test_logger", should_log=False
            )

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", "tests.test_logger")

        with Client.scoped_context({"user": {"email_suffix": "hotmail.com"}}):
            logger.debug("Test debug")
            assert_logged(capsys, "DEBUG", "Test debug", "tests.test_logger")

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", "tests.test_logger")

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", "tests.test_logger")

    def test_log_eval_rules_on_key_path(self, config_client, capsys):
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
            collect_sync_interval=None,
        )
        client = Client(options)

        client.config_client().config_resolver.local_store[config.key] = {
            "config": config
        }
        client.config_client().config_resolver.project_env_id = project_env_id

        (logger, ch) = configure_logger()
        filter = LoggerFilter(client.config_client(), prefix=client.options.log_prefix)
        ch.addFilter(filter)

        with Client.scoped_context({}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "DEBUG",
                "Test debug",
                "my.own.prefix.*tests.test_logger",
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(
                capsys, "INFO", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "ERROR", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"email_suffix": "yahoo.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "DEBUG",
                "Test debug",
                "my.own.prefix.*tests.test_logger",
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(
                capsys, "INFO", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "ERROR", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"email_suffix": "hotmail.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "DEBUG", "Test debug", "my.own.prefix.*tests.test_logger"
            )

            logger.info("Test info")
            assert_logged(
                capsys, "INFO", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "ERROR", "Test error", "my.own.prefix.*tests.test_logger"
            )

        with Client.scoped_context({"user": {"tracking_id": "user:4567"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys, "DEBUG", "Test debug", "my.own.prefix.*tests.test_logger"
            )

            logger.info("Test info")
            assert_logged(
                capsys, "INFO", "Test info", "my.own.prefix.*tests.test_logger"
            )

            logger.error("Test error")
            assert_logged(
                capsys, "ERROR", "Test error", "my.own.prefix.*tests.test_logger"
            )

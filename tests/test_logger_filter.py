from prefab_cloud_python import Client, Options, LoggerFilter
import logging
import pytest
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


def assert_logged(cap, level, msg, logger_name, should_log=True):
    # eg '2024-02-07 16:46:27,926 - root - INFO - Test info\n'
    pattern = re.compile(f".*{logger_name or 'root'}.*{level}.*{msg}.*")
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


def configure_logger(logger_name=None):
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)

    return (logger, ch)


class TestLoggerFilter:
    def test_get_severity(self, config_client):
        filter = LoggerFilter(config_client)

        assert filter._get_severity("") == Prefab.LogLevel.Value("WARN")
        assert filter._get_severity("app") == Prefab.LogLevel.Value("ERROR")
        assert filter._get_severity("app.controller") == Prefab.LogLevel.Value("ERROR")
        assert filter._get_severity("app.controller.hello") == Prefab.LogLevel.Value(
            "WARN"
        )
        assert filter._get_severity(
            "app.controller.hello.index"
        ) == Prefab.LogLevel.Value("INFO")
        assert filter._get_severity(
            "app.controller.hello.index.store"
        ) == Prefab.LogLevel.Value("INFO")
        assert filter._get_severity(
            "app.controller.hello.edit"
        ) == Prefab.LogLevel.Value("WARN")

    def test_capture_output(self, config_client, capsys):
        (logger, ch) = configure_logger()
        filter = LoggerFilter(client=config_client)
        ch.addFilter(filter)

        log_message = "capture this message"
        logger.warning(log_message)

        captured = capsys.readouterr()
        assert log_message in captured.out

    def test_no_output_for_lower_log_level(self, config_client, capsys):
        (logger, ch) = configure_logger()
        filter = LoggerFilter(client=config_client)
        ch.addFilter(filter)

        logger.debug("ok")

        captured = capsys.readouterr()
        assert captured.out == ""

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

        (logger, ch) = configure_logger(logger_name="tests.test_logger")
        filter = LoggerFilter(client=config_client)
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

    def test_log_eval_rules_on_key_path_for_standard_logger(
        self, config_client, capsys
    ):
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs=["unit_tests"],
            prefab_datasources="LOCAL_ONLY",
            collect_sync_interval=None,
        )
        client = Client(options)

        client.config_client().config_resolver.local_store[LoggingConfig.key] = {
            "config": LoggingConfig
        }
        client.config_client().config_resolver.project_env_id = project_env_id

        logger_name = "my.module.name"

        (logger, ch) = configure_logger(logger_name=logger_name)
        filter = LoggerFilter(client=client.config_client())
        ch.addFilter(filter)

        with Client.scoped_context({}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "DEBUG",
                "Test debug",
                logger_name,
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", logger_name)

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", logger_name)

        with Client.scoped_context({"user": {"email_suffix": "yahoo.com"}}):
            logger.debug("Test debug")
            assert_logged(
                capsys,
                "DEBUG",
                "Test debug",
                logger_name,
                should_log=False,
            )

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", logger_name)

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", logger_name)

        with Client.scoped_context({"user": {"email_suffix": "hotmail.com"}}):
            logger.debug("Test debug")
            assert_logged(capsys, "DEBUG", "Test debug", logger_name)

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", logger_name)

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", logger_name)

        with Client.scoped_context({"user": {"tracking_id": "user:4567"}}):
            logger.debug("Test debug")
            assert_logged(capsys, "DEBUG", "Test debug", logger_name)

            logger.info("Test info")
            assert_logged(capsys, "INFO", "Test info", logger_name)

            logger.error("Test error")
            assert_logged(capsys, "ERROR", "Test error", logger_name)


LoggingConfig = config = Prefab.Config(
    key="log-level.my.module.name",
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
                                string_list=Prefab.StringList(values=["user:4567"])
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

import logging
import os
from unittest.mock import patch

import pytest
import yaml

from prefab_cloud_python import Options, Client
from prefab_cloud_python.context import Context
import prefab_pb2 as Prefab
from prefab_cloud_python.config_client import (
    InitializationTimeoutException,
    MissingDefaultException,
)
from prefab_cloud_python.config_value_unwrapper import (
    EnvVarParseException,
    MissingEnvVarException,
)
from prefab_cloud_python.config_value_wrapper import ConfigValueWrapper
from prefab_cloud_python.encryption import DecryptionException
from tests.helpers import get_telemetry_events_by_type, sort_proto_loggers

LLV = Prefab.LogLevel.Value

CustomExceptions = {
    "unable_to_decrypt": DecryptionException,
    "missing_env_var": MissingEnvVarException,
    "initialization_timeout": InitializationTimeoutException,
    "unable_to_coerce_env_var": EnvVarParseException,
    "missing_default": MissingDefaultException,
}

LogLevels = {
    "debugs": logging.DEBUG,
    "infos": logging.INFO,
    "warns": logging.WARNING,
    "errors": logging.ERROR,
}

OnConnectionFailure = {":raise": "RAISE", ":return": "RETURN"}

ContextUploadMode = {
    ":none": Options.ContextUploadMode.NONE,
    ":shape_only": Options.ContextUploadMode.SHAPE_ONLY,
    ":periodic_example": Options.ContextUploadMode.PERIODIC_EXAMPLE,
}


def build_options_with_overrides(options, overrides):
    if overrides is None:
        return options
    if overrides.get("on_no_default") == 2:
        options.on_no_default = "RETURN_NONE"
    if overrides.get("namespace") is not None:
        options.namespace = overrides["namespace"]
    on_connection_failure = overrides.get("on_init_failure")
    if on_connection_failure:
        if on_connection_failure not in OnConnectionFailure:
            raise Exception(
                f"value of on_init_failure {on_connection_failure} maps to no known value"
            )
        options.on_connection_failure = OnConnectionFailure[on_connection_failure]
    options.connection_timeout_seconds = overrides.get(
        "initialization_timeout_sec", options.connection_timeout_seconds
    )
    if overrides.get("context_upload_mode"):
        options.context_upload_mode = ContextUploadMode[
            overrides["context_upload_mode"]
        ]
    return options


TEST_PATH = "./tests/prefab-cloud-integration-test-data/tests/0.2.4.3/"


@pytest.fixture
def options():
    return Options(
        api_key=os.environ["PREFAB_INTEGRATION_TEST_API_KEY"],
        prefab_api_url="https://api.staging-prefab.cloud",
        collect_sync_interval=None,
    )


def load_test_cases_from_file(filename):
    test_cases = []
    with open(TEST_PATH + filename) as f:
        yaml_data = yaml.safe_load(f.read())
    for test_set in yaml_data["tests"]:
        test_info = {
            "name": test_set.get("name") or "",
            "globalContext": test_set.get("context"),
            "fileName": filename,
        }
        for case in test_set["cases"]:
            test_cases.append(
                {"testInfo": test_info, "name": case.get("name"), "case": case}
            )
    return test_cases


def make_id_from_test_case(test_case_dict):
    test_info = test_case_dict["testInfo"]
    return f"{test_info.get('fileName')}__{test_info.get('name')}__{test_case_dict.get('name')}".replace(
        " ", "_"
    )


def run_test(
    test,
    options,
    input_key="key",
    function="get",
    global_context=None,
    expected_modifier=(lambda x: x),
):
    case = test["case"]
    input = case["input"]
    expected = case["expected"]
    options = build_options_with_overrides(options, case.get("client_overrides"))
    with Client(options) as client:
        if global_context:
            Context.set_current(Context(global_context))
        key = input[input_key]
        default = input.get("default")
        if input.get("context"):
            context = Context(input["context"])
        else:
            context = None
        if function == "get":
            if expected.get("status") == "raise":
                with pytest.raises(
                    CustomExceptions.get(expected["error"] or Exception)
                ):
                    client.get(key, context=context)
            else:
                assert client.get(
                    key, default=default, context=context
                ) == expected_modifier(expected["value"])
        elif function == "enabled":
            assert client.enabled(key, context=context) == expected_modifier(
                expected["value"]
            )
        elif function == "post":
            pytest.fail("post not implemented")


def run_telemetry_test(test, options, global_context=None):
    case = test["case"]
    options = build_options_with_overrides(options, case.get("client_overrides"))
    if global_context:
        Context.set_current(Context(global_context))
    client = Client(options)
    with patch.object(client, "post", wraps=client.post) as spy_method:
        if case["aggregator"] == "log_path":
            run_logging_telemetry_test(test, case, client, spy_method)
        elif case["aggregator"] == "context_shape":
            run_context_shape_telemetry_test(test, case, client, spy_method)
        elif case["aggregator"] == "example_contexts":
            run_context_instances_telemetry_test(test, case, client, spy_method)
        elif case["aggregator"] == "evaluation_summary":
            run_evaluation_summary_telemetry_test(test, case, client, spy_method)
        else:
            pytest.fail(f"aggregator {case['aggregator']} not implemented")


def run_logging_telemetry_test(test, case, client, spy_post_method):
    for logger_data in case["data"]:
        for level, count in logger_data["counts"].items():
            for _ in range(count):
                client.record_log(logger_data["logger_name"], LogLevels[level])
    client.telemetry_manager.flush_and_block()
    url, telemetry_events = spy_post_method.call_args.args
    assert url == "/api/v1/telemetry/"
    telemetry_events_by_type = get_telemetry_events_by_type(telemetry_events)
    log_events = telemetry_events_by_type["loggers"]
    assert len(log_events) == 1
    expected_protos = sort_proto_loggers(
        build_loggers_expected_data(case["expected_data"])
    )
    assert sort_proto_loggers(log_events[0].loggers) == expected_protos


def run_context_shape_telemetry_test(test, case, client, spy_post_method):
    context = Context(case["data"])
    client.config_client().get("some-key", default=10, context=context)
    client.telemetry_manager.flush_and_block()
    url, telemetry_events = spy_post_method.call_args.args
    expected_shapes = [
        Prefab.ContextShape(name=item["name"], field_types=item["field_types"])
        for item in case["expected_data"]
    ]
    assert url == "/api/v1/telemetry/"
    actual_shapes = get_telemetry_events_by_type(telemetry_events)["context_shapes"]
    for expected_shape in expected_shapes:
        assert expected_shape in actual_shapes[0].shapes


def run_context_instances_telemetry_test(test, case, client, spy_post_method):
    context = Context(case["data"])
    expected_context_proto = Context(case["expected_data"]).to_proto()
    client.config_client().get("some-key", default=10, context=context)
    client.telemetry_manager.flush_and_block()
    url, telemetry_events = spy_post_method.call_args.args
    assert url == "/api/v1/telemetry/"
    actual_context = get_telemetry_events_by_type(telemetry_events)["example_contexts"]
    for expected_context in expected_context_proto.contexts:
        assert expected_context in actual_context[0].examples[0].contextSet.contexts


def run_evaluation_summary_telemetry_test(test, case, client, spy_post_method):
    for key in case["data"]:
        client.config_client().get(key)
    client.telemetry_manager.flush_and_block()
    url, telemetry_events = spy_post_method.call_args.args
    assert url == "/api/v1/telemetry/"
    actual_summary_protos = get_telemetry_events_by_type(telemetry_events)["summaries"][
        0
    ].summaries
    expected_summary_protos = build_evaluation_summary_expected_data(
        case["expected_data"]
    )
    assert clear_config_ids(actual_summary_protos) == clear_config_ids(
        expected_summary_protos
    )


def clear_config_ids(summary_list):
    for summary in summary_list:
        for counter in summary.counters:
            counter.config_id = 0


def build_loggers_expected_data(expected_data):
    loggers_expected_data = []
    for logger_data in expected_data:
        current_logger = Prefab.Logger(logger_name=logger_data["logger_name"])
        for level, count in logger_data["counts"].items():
            setattr(current_logger, level, count)
        loggers_expected_data.append(current_logger)
    return loggers_expected_data


def build_evaluation_summary_expected_data(expected_data):
    summaries = []
    for expected_datum in expected_data:
        counts = [
            Prefab.ConfigEvaluationCounter(
                count=expected_datum["count"],
                config_row_index=expected_datum["summary"]["config_row_index"],
                conditional_value_index=expected_datum["summary"][
                    "conditional_value_index"
                ],
                weighted_value_index=expected_datum.get("weighted_value_index"),
                selected_value=ConfigValueWrapper.wrap(expected_datum["value"]),
            )
        ]
        summaries.append(
            Prefab.ConfigEvaluationSummary(
                key=expected_datum["key"], type=expected_datum["type"], counters=counts
            )
        )
    return summaries


class TestIntegration:
    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("enabled.yaml"),
        ids=make_id_from_test_case,
    )
    def test_enabled(self, options, testcase):
        run_test(testcase, options, input_key="flag", function="enabled")

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("enabled_with_contexts.yaml"),
        ids=make_id_from_test_case,
    )
    def test_enabled_with_contexts(self, options, testcase):
        run_test(
            testcase,
            options,
            input_key="flag",
            function="enabled",
            global_context=testcase["testInfo"].get("globalContext"),
        )

    @pytest.mark.parametrize(
        "testcase", load_test_cases_from_file("get.yaml"), ids=make_id_from_test_case
    )
    def test_get(self, options, testcase):
        run_test(testcase, options)

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("get_feature_flag.yaml"),
        ids=make_id_from_test_case,
    )
    def test_get_feature_flag(self, options, testcase):
        run_test(testcase, options, input_key="flag")

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("get_log_level.yaml"),
        ids=make_id_from_test_case,
    )
    def test_get_log_level(self, options, testcase):
        run_test(
            testcase,
            options,
            global_context=testcase["testInfo"].get("globalContext"),
            expected_modifier=(lambda x: LLV(x)),
        )

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("get_or_raise.yaml"),
        ids=make_id_from_test_case,
    )
    def test_get_or_raise(self, options, testcase):
        run_test(testcase, options)

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("get_weighted_values.yaml"),
        ids=make_id_from_test_case,
    )
    def test_get_weighted_values(self, options, testcase):
        run_test(testcase, options, input_key="flag")

    @pytest.mark.parametrize(
        "testcase",
        load_test_cases_from_file("post.yaml"),
        ids=make_id_from_test_case,
    )
    def test_post(self, options, testcase):
        run_telemetry_test(testcase, options)

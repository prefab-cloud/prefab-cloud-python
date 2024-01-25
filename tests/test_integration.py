import os

import pytest
import yaml

from prefab_cloud_python import Options, Client, Context
import prefab_pb2 as Prefab
from prefab_cloud_python.config_client import InitializationTimeoutException
from prefab_cloud_python.config_value_unwrapper import (
    EnvVarParseException,
    MissingEnvVarException,
)
from prefab_cloud_python.encryption import DecryptionException

LLV = Prefab.LogLevel.Value

CustomExceptions = {
    "unable_to_decrypt": DecryptionException,
    "missing_env_var": MissingEnvVarException,
    "initialization_timeout": InitializationTimeoutException,
    "unable_to_coerce_env_var": EnvVarParseException,
    "missing_default": Exception,
}

OnConnectionFailure = {":raise": "RAISE", ":return": "RETURN"}


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
    return options


TEST_PATH = "./tests/prefab-cloud-integration-test-data/tests/0.2.4.2/"


@pytest.fixture
def options():
    return Options(
        api_key=os.environ["PREFAB_INTEGRATION_TEST_API_KEY"],
        prefab_api_url="https://api.staging-prefab.cloud",
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
    client = Client(options)
    if global_context:
        Context.set_current(Context(global_context))
    key = input[input_key]
    default = input.get("default")
    if input.get("context"):
        context = Context(input["context"])
    else:
        context = "NO_CONTEXT_PROVIDED"
    if function == "get":
        if expected.get("status") == "raise":
            with pytest.raises(CustomExceptions.get(expected["error"] or Exception)):
                client.get(key, context=context)
        else:
            assert client.get(
                key, default=default, context=context
            ) == expected_modifier(expected["value"])
    elif function == "enabled":
        assert client.enabled(key, context=context) == expected_modifier(
            expected["value"]
        )


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

import os
import pytest
import yaml

from prefab_cloud_python import Options, Client, Context
import prefab_pb2 as Prefab

LLV = Prefab.LogLevel.Value


def build_options_with_overrides(options, overrides):
    if overrides is None:
        return options
    if overrides.get("on_no_default") == 2:
        options.on_no_default = "RETURN_NONE"
    if overrides.get("namespace") is not None:
        options.namespace = overrides["namespace"]
    return options


TEST_PATH = "./tests/prefab-cloud-integration-test-data/tests/0.2.1/"


@pytest.fixture
def options():
    return Options(
        api_key=os.environ["PREFAB_INTEGRATION_TEST_API_KEY"],
        prefab_api_url="https://api.staging-prefab.cloud",
    )


def run_test(
    test,
    options,
    input_key="key",
    function="get",
    global_context=None,
    expected_modifier=(lambda x: x),
):
    input = test["input"]
    expected = test["expected"]
    options = build_options_with_overrides(options, test.get("client_overrides"))
    client = Client(options)
    if global_context:
        Context.set_current(global_context)
    key = input[input_key]
    default = input.get("default")
    if input.get("context"):
        context = Context(input["context"])
    else:
        context = "NO_CONTEXT_PROVIDED"
    if function == "get":
        if expected.get("status") == "raise":
            with pytest.raises(Exception) as exception:
                client.get(key, context=context)
                assert expected["message"] in str(exception)
        else:
            assert client.get(
                key, default=default, context=context
            ) == expected_modifier(expected["value"])
    elif function == "enabled":
        assert client.enabled(key, context=context) == expected_modifier(
            expected["value"]
        )


class TestItegration:
    def test_enabled(self, options):
        with open(TEST_PATH + "enabled.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            for test in test_set["cases"]:
                run_test(test, options, input_key="flag", function="enabled")

    def test_enabled_with_contexts(self, options):
        with open(TEST_PATH + "enabled_with_contexts.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            global_context = Context(test_set["context"])
            for test in test_set["cases"]:
                run_test(
                    test,
                    options,
                    input_key="flag",
                    function="enabled",
                    global_context=global_context,
                )

    def test_get(self, options):
        with open(TEST_PATH + "get.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            for test in test_set["cases"]:
                run_test(test, options)

    def test_get_feature_flag(self, options):
        with open(TEST_PATH + "get_feature_flag.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            for test in test_set["cases"]:
                run_test(test, options, input_key="flag")

    def test_get_log_level(self, options):
        with open(TEST_PATH + "get_log_level.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            if test_set.get("context"):
                global_context = Context(test_set["context"])
            else:
                global_context = None
            for test in test_set["cases"][:1]:
                run_test(
                    test,
                    options,
                    global_context=global_context,
                    expected_modifier=(lambda x: LLV(x)),
                )

    def test_get_or_raise(self, options):
        with open(TEST_PATH + "get_or_raise.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            for test in test_set["cases"]:
                run_test(test, options)

    def test_get_weighted_values(self, options):
        with open(TEST_PATH + "get_weighted_values.yaml") as f:
            yaml_data = yaml.safe_load(f.read())
        for test_set in yaml_data["tests"]:
            for test in test_set["cases"]:
                run_test(test, options, input_key="flag")

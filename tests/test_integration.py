import glob
import os
import pytest
import yaml

from prefab_cloud_python import Options, Client


def build_options_with_overrides(options, overrides):
    if overrides is None:
        return options
    if overrides.get("on_no_default") == 2:
        options.on_no_default = "RETURN_NONE"
    if overrides.get("namespace") is not None:
        options.namespace = overrides["namespace"]
    return options


def find_integration_test_files():
    return glob.glob("./tests/prefab-cloud-integration-test-data/tests/0.1.2/*.yaml")


@pytest.fixture
def options():
    return Options(
        api_key=os.environ["PREFAB_INTEGRATION_TEST_API_KEY"],
        prefab_api_url="https://api.staging-prefab.cloud",
        prefab_grpc_url="grpc.staging-prefab.cloud:443",
        namespace="test-namespace"
    )


class TestItegration:
    # def test_get(self, options):
    #     f = open("./tests/prefab-cloud-integration-test-data/tests/0.1.2/get.yaml", "r")
    #     yaml_data = yaml.safe_load(f.read())
    #     f.close()
    #     for test in yaml_data["tests"][4:]:
    #         self.run_test(test, options)

    def test_get_feature_flags(self, options):
        f = open("./tests/prefab-cloud-integration-test-data/tests/0.1.2/get_feature_flag.yaml", "r")
        yaml_data = yaml.safe_load(f.read())
        f.close()
        for test in yaml_data["tests"]:
            self.run_test(test, options, input_key="flag")

    def run_test(self, test, options, input_key="key"):
        options = build_options_with_overrides(options, test.get("client_overrides"))
        print(test["name"], " :: ", options.namespace)
        client = Client(options)
        key = test["input"][input_key]
        default = test["input"].get("default")
        assert client.get(key, default=default) == test["expected"]["value"]

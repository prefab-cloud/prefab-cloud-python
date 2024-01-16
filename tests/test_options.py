from prefab_cloud_python import Options
from prefab_cloud_python.options import (
    MissingApiKeyException,
    InvalidApiKeyException,
    InvalidApiUrlException,
    InvalidGrpcUrlException,
)

import os
import pytest

from contextlib import contextmanager


@contextmanager
def extended_env(new_env_vars):
    old_env = os.environ.copy()
    os.environ.update(new_env_vars)
    yield
    os.environ.clear()
    os.environ.update(old_env)


class TestOptionsApiKey:
    def test_valid_api_key_from_input(self):
        options = Options(api_key="1-dev-api-key")
        assert options.api_key == "1-dev-api-key"
        assert options.api_key_id == "1"

    def test_valid_api_key_from_env(self):
        with extended_env({"PREFAB_API_KEY": "2-test-api-key"}):
            options = Options()

            assert options.api_key == "2-test-api-key"
            assert options.api_key_id == "2"

    def test_api_key_from_input_overrides_env(self):
        with extended_env({"PREFAB_API_KEY": "2-test-api-key"}):
            options = Options(api_key="3-dev-api-key")

            assert options.api_key == "3-dev-api-key"
            assert options.api_key_id == "3"

    def test_missing_api_key_error(self):
        with pytest.raises(MissingApiKeyException) as context:
            Options()

        assert "No API key found" in str(context)

    def test_invalid_api_key_error(self):
        with pytest.raises(InvalidApiKeyException) as context:
            Options(api_key="bad_api_key")
            assert "Invalid API key: bad_api_key" in str(context)

    def test_api_key_doesnt_matter_local_only_set_in_env(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(api_key="bad_api_key")
            assert options.api_key is None
            assert options.api_key_id == "local"

    def test_api_key_doesnt_matter_local_only(self):
        options = Options(api_key="bad_api_key", prefab_datasources="LOCAL_ONLY")
        assert options.api_key is None


class TestOptionsApiUrl:
    def test_prefab_api_url_from_env(self):
        with extended_env(
            {
                "PREFAB_API_KEY": "1-api",
                "PREFAB_API_URL": "https://api.dev-prefab.cloud",
            }
        ):
            options = Options()
            assert options.prefab_api_url == "https://api.dev-prefab.cloud"

    def test_api_url_from_input(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            options = Options(prefab_api_url="https://api.test-prefab.cloud")
            assert options.prefab_api_url == "https://api.test-prefab.cloud"

    def test_prefab_api_url_default_fallback(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            options = Options()
            assert options.prefab_api_url == "https://api.prefab.cloud"

    def test_prefab_api_url_errors_on_invalid_format(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            with pytest.raises(InvalidApiUrlException) as context:
                Options(prefab_api_url="httttp://api.prefab.cloud")

            assert "Invalid API URL found: httttp://api.prefab.cloud" in str(context)

    def test_prefab_api_url_doesnt_matter_local_only_set_in_env(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(prefab_api_url="http://api.prefab.cloud")
            assert options.prefab_api_url is None

    def test_prefab_api_url_doesnt_matter_local_only(self):
        options = Options(
            prefab_api_url="http://api.prefab.cloud", prefab_datasources="LOCAL_ONLY"
        )
        assert options.prefab_api_url is None


class TestOptionsGrpcUrl:
    def test_prefab_grpc_url_from_env(self):
        with extended_env(
            {"PREFAB_API_KEY": "1-api", "PREFAB_GRPC_URL": "grpc.dev-prefab.cloud"}
        ):
            options = Options()
            assert options.prefab_grpc_url == "grpc.dev-prefab.cloud"

    def test_grpc_url_from_input(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            options = Options(prefab_grpc_url="grpc.test-prefab.cloud")
            assert options.prefab_grpc_url == "grpc.test-prefab.cloud"

    def test_prefab_grpc_url_default_fallback(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            options = Options()
            assert options.prefab_grpc_url == "grpc.prefab.cloud:443"

    def test_prefab_grpc_url_errors_on_invalid_format(self):
        with extended_env({"PREFAB_API_KEY": "1-api"}):
            with pytest.raises(InvalidGrpcUrlException) as context:
                Options(prefab_grpc_url="gprc.prefab.cloud")

        assert "Invalid gRPC URL found: gprc.prefab.cloud" in str(context)

    def test_prefab_grpc_url_doesnt_matter_local_only_set_in_env(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(prefab_grpc_url="gprc.prefab.cloud")
            assert options.prefab_grpc_url is None

    def test_prefab_grpc_url_doesnt_matter_local_only(self):
        options = Options(
            prefab_grpc_url="gprc.prefab.cloud", prefab_datasources="LOCAL_ONLY"
        )
        assert options.prefab_grpc_url is None


class TestOptionsPrefabEnvs:
    def test_reads_single_value_from_options(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(prefab_envs="testing")
            assert options.prefab_envs == ["testing"]

    def test_list_read_from_options(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(prefab_envs=["testing", "unit_tests"])
            assert options.prefab_envs == ["testing", "unit_tests"]

    def test_read_csl_from_options(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(prefab_envs="testing, unit_tests")
            assert options.prefab_envs == ["testing", "unit_tests"]

    def test_read_from_env(self):
        with extended_env(
            {"PREFAB_DATASOURCES": "LOCAL_ONLY", "PREFAB_ENVS": "testing, unit_tests"}
        ):
            options = Options()
            assert options.prefab_envs == ["testing", "unit_tests"]

    def test_merge_env_and_options(self):
        with extended_env(
            {
                "PREFAB_DATASOURCES": "LOCAL_ONLY",
                "PREFAB_ENVS": "development, unit_tests",
            }
        ):
            options = Options(prefab_envs="testing")
            assert options.prefab_envs == ["development", "testing", "unit_tests"]


class TestOptionsCdnUrl:
    def test_is_none_when_local_only(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options()
            assert options.url_for_api_cdn is None

    def test_formats_from_the_api_url(self):
        with extended_env(
            {
                "PREFAB_API_KEY": "2-test-api-key",
                "PREFAB_API_URL": "https://api.staging-prefab.cloud",
            }
        ):
            options = Options()
            assert (
                options.url_for_api_cdn
                == "https://api-staging-prefab-cloud.global.ssl.fastly.net"
            )

    def test_prefers_to_read_from_env(self):
        with extended_env(
            {
                "PREFAB_API_KEY": "2-test-api-key",
                "PREFAB_API_URL": "https://api.staging-prefab.cloud",
                "PREFAB_CDN_URL": "prefab-cdn-url",
            }
        ):
            options = Options()
            assert options.url_for_api_cdn == "prefab-cdn-url"


class TestOptionsOnNoDefault:
    def test_defaults_to_raise(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options()
            assert options.on_no_default == "RAISE"

    def test_returns_return_none_if_given(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(on_no_default="RETURN_NONE")
            assert options.on_no_default == "RETURN_NONE"

    def test_returns_raise_for_any_other_input(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(on_no_default="WHATEVER")
            assert options.on_no_default == "RAISE"


class TestOptionsOnConnectionFailure:
    def test_defaults_to_return(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options()
            assert options.on_connection_failure == "RETURN"

    def test_returns_raise_if_given(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(on_connection_failure="RAISE")
            assert options.on_connection_failure == "RAISE"

    def test_returns_return_for_any_other_input(self):
        with extended_env({"PREFAB_DATASOURCES": "LOCAL_ONLY"}):
            options = Options(on_connection_failure="WHATEVER")
            assert options.on_connection_failure == "RETURN"


class TestOptionsLogCollection:
    def test_has_a_default(self):
        with extended_env({"PREFAB_API_KEY": "2-test-api-key"}):
            options = Options()
            assert options.collect_logs is True
            assert options.collect_max_paths == 1000
            assert options.collect_sync_interval is None

    def test_can_be_set(self):
        with extended_env({"PREFAB_API_KEY": "2-test-api-key"}):
            options = Options(collect_max_paths=100, collect_sync_interval=1000)
            assert options.collect_max_paths == 100
            assert options.collect_sync_interval == 1000

    def test_is_zero_if_local_only(self):
        options = Options(prefab_datasources="LOCAL_ONLY", collect_max_paths=100)
        assert options.collect_max_paths == 0

    def test_is_zero_if_collect_logs_is_false(self):
        with extended_env({"PREFAB_API_KEY": "2-test-api-key"}):
            options = Options(collect_logs=False, collect_max_paths=100)
            assert options.collect_max_paths == 0

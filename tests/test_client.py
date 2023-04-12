from prefab_cloud_python import Options, Client
from prefab_cloud_python.config_client import MissingDefaultException
import pytest


@pytest.fixture
def client():
    options = Options(
        prefab_config_classpath_dir="tests",
        prefab_envs=["unit_tests"],
        prefab_datasources="LOCAL_ONLY",
    )
    return Client(options)


class TestClient:
    def test_get(self, client):
        assert client.get("sample") == "test sample value"
        assert client.get("sample_int") == 123

    def test_get_with_default(self, client):
        assert not client.get("false_value", default="red")
        assert client.get("zero_value", default="red") == 0
        assert client.get("missing_value", default="buckets") == "buckets"

    def test_get_with_missing_default(self, client):
        with pytest.raises(MissingDefaultException) as exception:
            assert client.get("missing_value") is None

        assert "No value found for key 'missing_value'" in str(exception)
        assert "on_no_default" in str(exception)

    def test_can_be_configured_to_return_none_when_missing_default(self, client):
        options = client.options
        options.on_no_default = "RETURN_NONE"
        client = Client(options)

        assert client.get("missing_value") is None

    def test_enabled(self, client):
        assert not client.enabled("does_not_exist")
        assert client.enabled("enabled_flag")
        assert not client.enabled("disabled_flag")
        assert not client.enabled("flag_with_a_value")

    def test_enabled_with_lookup_key(self, client):
        assert not client.enabled("in_lookup_key", "jimmy")
        assert client.enabled("in_lookup_key", "abc123")
        assert client.enabled("in_lookup_key", "xyz987")

    def test_ff_get_with_lookup_key(self, client):
        assert client.get("in_lookup_key", lookup_key="jimmy") is None
        assert client.get("in_lookup_key", "DEFAULT", "jimmmy", {}) == "DEFAULT"
        assert client.get("in_lookup_key", "abc123")
        assert client.get("in_lookup_key", "xyz9987")

    def test_ff_enabled_with_attributes(self, client):
        assert not client.enabled(
            "just_my_domain", lookup_key="abc123", attributes={"domain": "gmail.com"}
        )
        assert not client.enabled(
            "just_my_domain", lookup_key="abc123", attributes={"domain": "prefab.cloud"}
        )
        assert not client.enabled(
            "just_my_domain", lookup_key="abc123", attributes={"domain": "example.com"}
        )

    def test_ff_get_with_attributes(self, client):
        assert (
            client.get(
                "just_my_domain",
                lookup_key="abc123",
                properties={"domain": "gmail.com"},
            )
            is None
        )
        assert (
            client.get(
                "just_my_domain",
                lookup_key="abc123",
                properties={"domain": "gmail.com"},
                default="DEFAULT",
            )
            == "DEFAULT"
        )
        assert (
            client.get(
                "just_my_domain",
                lookup_key="abc123",
                properties={"domain": "prefab.cloud"},
            )
            == "new-version"
        )
        assert (
            client.get(
                "just_my_domain",
                lookup_key="abc123",
                properties={"domain": "example.com"},
            )
            == "new-version"
        )

    def test_getting_feature_flag_value(self, client):
        assert not client.enabled("flag_with_a_value")
        assert client.get("flag_with_a_value") == "all-features"

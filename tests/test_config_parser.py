from prefab_cloud_python.config_parser import ConfigParser
from prefab_cloud_python.config_value_unwrapper import ConfigValueUnwrapper
import prefab_pb2 as Prefab

file_name = "example-config.yaml"
default_match = "default"


class TestConfigParser:
    def test_parse_int(self):
        key = "sample_int"
        parsed = ConfigParser.parse(key, 123, {}, file_name)[key]

        config = parsed["config"]

        assert parsed["source"] == file_name
        assert parsed["match"] == default_match
        assert config.config_type == Prefab.ConfigType.keys().index("CONFIG")
        assert config.key == key
        assert len(config.rows) == 1
        assert len(config.rows[0].values) == 1
        assert config.rows[0].values[0].value.int == 123

    def test_parse_map(self):
        key = "nested"
        value = {"_": "top level", "string": "nested value", "int": 123}
        parsed = ConfigParser.parse(key, value, {}, file_name)

        top_level = parsed[key]
        assert top_level["source"] == file_name
        assert top_level["match"] == default_match
        assert top_level["config"].config_type == Prefab.ConfigType.keys().index(
            "CONFIG"
        )
        assert top_level["config"].key == key
        assert top_level["config"].rows[0].values[0].value.string == "top level"

        nested_string = parsed["nested.string"]
        assert nested_string["source"] == file_name
        assert nested_string["match"] == default_match
        assert nested_string["config"].config_type == Prefab.ConfigType.keys().index(
            "CONFIG"
        )
        assert nested_string["config"].key == "nested.string"
        assert nested_string["config"].rows[0].values[0].value.string == "nested value"

        nested_int = parsed["nested.int"]
        assert nested_int["source"] == file_name
        assert nested_int["match"] == default_match
        assert nested_int["config"].config_type == Prefab.ConfigType.keys().index(
            "CONFIG"
        )
        assert nested_int["config"].key == "nested.int"
        assert nested_int["config"].rows[0].values[0].value.int == 123

    def test_parse_feature_flag(self):
        key = "sample_flag"
        flag = {"feature_flag": True, "value": "sample value"}

        parsed = ConfigParser.parse(key, flag, {}, file_name)[key]
        config = parsed["config"]

        assert parsed["source"] == file_name
        assert parsed["match"] == key
        assert config.config_type == Prefab.ConfigType.keys().index("FEATURE_FLAG")
        assert config.key == key
        assert len(config.rows) == 1
        assert len(config.rows[0].values) == 1

        value_row = config.rows[0].values[0]

        assert isinstance(value_row.value.weighted_values, Prefab.WeightedValues)
        assert ConfigValueUnwrapper.unwrap(value_row.value, key, {}) == "sample value"

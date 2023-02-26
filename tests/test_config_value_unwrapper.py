from prefab_cloud_python.config_value_unwrapper import ConfigValueUnwrapper
import prefab_pb2 as Prefab

config_key = "config_key"

class TestConfigValueUnwrapper:
    def test_unwrapping_int(self):
        config_value = Prefab.ConfigValue(int=123)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == 123

    def test_unwrapping_string(self):
        config_value = Prefab.ConfigValue(string="abc")
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == "abc"

    def test_unwrapping_double(self):
        config_value = Prefab.ConfigValue(double=5.22)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == 5.22

    def test_unwrapping_bool(self):
        config_value = Prefab.ConfigValue(bool=True)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == True

        config_value = Prefab.ConfigValue(bool=False)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == False

    def test_unwrapping_log_level(self):
        config_value = Prefab.ConfigValue(log_level="INFO")
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == Prefab.LogLevel.keys().index("INFO")

    def test_unwrapping_string_list(self):
        string_list = ["a", "b", "c"]
        config_value = Prefab.ConfigValue(string_list=Prefab.StringList(values=string_list))
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == string_list

    def test_unwrapping_weighted_values(self):
        weighted_values = self.build_weighted_values({"abc": 1})
        config_value = Prefab.ConfigValue(weighted_values=weighted_values)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {}) == "abc"

        weighted_values = self.build_weighted_values({"abc": 1, "def": 1, "ghi": 1})
        config_value = Prefab.ConfigValue(weighted_values=weighted_values)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:123"}) == "ghi"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:456"}) == "ghi"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:789"}) == "abc"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:012"}) == "def"

        weighted_values = self.build_weighted_values({"abc": 1, "def": 99, "ghi": 1})
        config_value = Prefab.ConfigValue(weighted_values=weighted_values)
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:123"}) == "def"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:456"}) == "def"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:789"}) == "def"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:012"}) == "def"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:103"}) == "ghi"
        assert ConfigValueUnwrapper.unwrap(config_value, config_key, {"LOOKUP": "user:119"}) == "abc"

    @staticmethod
    def build_weighted_values(values_and_weights):
        weighted_values = []
        for value in values_and_weights:
            weighted_value = Prefab.WeightedValue(
                value=Prefab.ConfigValue(string=value),
                weight=values_and_weights[value]
            )
            weighted_values.append(weighted_value)

        return Prefab.WeightedValues(weighted_values=weighted_values)


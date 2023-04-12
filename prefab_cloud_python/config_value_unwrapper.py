from .weighted_value_resolver import WeightedValueResolver


class UnknownConfigValueTypeException(Exception):
    "Raised when a config value of an unknown type is passed to the unwrapper"

    def __init__(self, type):
        super().__init__("Unknown config value type: %s" % type)


class ConfigValueUnwrapper:
    def unwrap(value, key, properties={}):
        if value is None:
            return None

        type = value.WhichOneof("type")

        if type in ["int", "string", "double", "bool", "log_level"]:
            return getattr(value, type)
        elif type == "string_list":
            return value.string_list.values
        elif type == "weighted_values":
            lookup_key = properties.get("LOOKUP")
            weights = value.weighted_values.weighted_values
            resolved_value = WeightedValueResolver(weights, key, lookup_key).resolve()
            return ConfigValueUnwrapper.unwrap(resolved_value.value, key, properties)
        else:
            raise UnknownConfigValueTypeException(type)

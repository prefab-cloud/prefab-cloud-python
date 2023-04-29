from .weighted_value_resolver import WeightedValueResolver
from .context import Context


class UnknownConfigValueTypeException(Exception):
    "Raised when a config value of an unknown type is passed to the unwrapper"

    def __init__(self, type):
        super().__init__("Unknown config value type: %s" % type)


class ConfigValueUnwrapper:
    def unwrap(value, key, context=Context.get_current()):
        if value is None:
            return None

        type = value.WhichOneof("type")

        if type in ["int", "string", "double", "bool", "log_level"]:
            return getattr(value, type)
        elif type == "string_list":
            return value.string_list.values
        elif type == "weighted_values":
            weights = value.weighted_values.weighted_values
            hash_value = context.get(value.weighted_values.hash_by_property_name)
            resolved_value = WeightedValueResolver(weights, key, hash_value).resolve()
            return ConfigValueUnwrapper.unwrap(resolved_value.value, key, context)
        else:
            raise UnknownConfigValueTypeException(type)

from .weighted_value_resolver import WeightedValueResolver
from .config_value_wrapper import ConfigValueWrapper
from .context import Context
import prefab_pb2 as Prefab
import yaml
import os


VTV = Prefab.Config.ValueType.Value
VTN = Prefab.Config.ValueType.Name


class EnvVarParseException(Exception):
    "Raised when an invalid value type is set for a `provided` config value"

    def __init__(self, env_var, config, env_var_name):
        super().__init__(
            "Evaluating %s couldn't coerce %s of %s to %s"
            % (config.key, env_var_name, env_var, VTN(config.value_type))
        )


class UnknownConfigValueTypeException(Exception):
    "Raised when a config value of an unknown type is passed to the unwrapper"

    def __init__(self, type):
        super().__init__("Unknown config value type: %s" % type)


class UnknownProvidedSourceException(Exception):
    "Raised when a provided value has an unknown source"

    def __init__(self, source):
        super().__init__("Unknown provided source: %s" % source)


class ConfigValueUnwrapper:
    def __init__(self, value, resolver, weighted_value_index=None):
        self.value = value
        self.resolve = resolver
        self.weighted_value_index = weighted_value_index

    def deepest_value(config_value, config, resolver, context=Context.get_current()):
        if config_value and config_value.WhichOneof("type") == "weighted_values":
            value, index = WeightedValueResolver(
                config_value.weighted_values.weighted_values,
                config.key,
                context.get(config_value.weighted_values.hash_by_property_name),
            ).resolve()
            return ConfigValueUnwrapper(
                ConfigValueUnwrapper.deepest_value(
                    value.value, config, resolver, context
                ).value,
                resolver,
                index,
            )
        elif config_value and config_value.WhichOneof("type") == "provided":
            if config_value.provided.source == Prefab.ProvidedSource.Value("ENV_VAR"):
                raw = os.getenv(config_value.provided.lookup)
                if raw is None:
                    resolver.base_client.logger.log_internal(
                        "warn",
                        f"ENV Variable {config_value.provided.lookup} not found. Using empty string.",
                    )
                    return ConfigValueUnwrapper(ConfigValueWrapper.wrap(""), resolver)
                else:
                    coerced = ConfigValueUnwrapper.coerce_into_type(
                        raw, config, config_value.provided.lookup
                    )
                    return ConfigValueUnwrapper(
                        ConfigValueWrapper.wrap(coerced), resolver
                    )
            else:
                raise UnknownProvidedSourceException(config_value.provided.source)

        else:
            return ConfigValueUnwrapper(config_value, resolver)

    def unwrap(self):
        if self.value is None:
            return None

        type = self.value.WhichOneof("type")

        if type in ["int", "string", "double", "bool", "log_level"]:
            return getattr(self.value, type)
        elif type == "string_list":
            return self.value.string_list.values
        else:
            raise UnknownConfigValueTypeException(type)

    def coerce_into_type(value_string, config, env_var_name):
        try:
            value_type = config.value_type
            if value_type == VTV("INT"):
                return int(value_string)
            if value_type == VTV("DOUBLE"):
                return float(value_string)
            elif value_type == VTV("STRING"):
                return str(value_string)
            elif value_type == VTV("STRING_LIST"):
                maybe_string_list = yaml.safe_load(value_string)
                if isinstance(maybe_string_list, list):
                    return maybe_string_list
                else:
                    raise EnvVarParseException(value_string, config, env_var_name)
            elif value_type == VTV("BOOL"):
                maybe_bool = yaml.safe_load(value_string)
                if maybe_bool is True or maybe_bool is False:
                    return maybe_bool
                else:
                    raise EnvVarParseException(value_string, config, env_var_name)
            elif value_type == VTV("NOT_SET_VALUE_TYPE"):
                return yaml.safe_load(value_string)
            else:
                raise EnvVarParseException(value_string, config, env_var_name)
        except ValueError:
            raise EnvVarParseException(value_string, config, env_var_name)

    # def self.coerce_into_type(value_string, config, env_var_name)
    #   case config.value_type
    #   when :INT then Integer(value_string)
    #   when :DOUBLE then Float(value_string)
    #   when :STRING then String(value_string)
    #   when :STRING_LIST then
    #     maybe_string_list = YAML.load(value_string)
    #     case maybe_string_list
    #     when Array
    #       maybe_string_list
    #     else
    #       raise raise Prefab::Errors::EnvVarParseError.new(value_string, config, env_var_name)
    #     end
    #   when :BOOL then
    #     maybe_bool = YAML.load(value_string)
    #     case maybe_bool
    #     when TrueClass, FalseClass
    #       maybe_bool
    #     else
    #       raise Prefab::Errors::EnvVarParseError.new(value_string, config, env_var_name)
    #     end
    #   when :NOT_SET_VALUE_TYPE
    #     YAML.load(value_string)
    #   else
    #     raise Prefab::Errors::EnvVarParseError.new(value_string, config, env_var_name)
    #   end
    # rescue ArgumentError

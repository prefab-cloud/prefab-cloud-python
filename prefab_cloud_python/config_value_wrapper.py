import prefab_pb2 as Prefab
import typing


class ConfigValueWrapper:
    def wrap(value: typing.Any, confidential: bool | None = None) -> Prefab.ConfigValue:
        if type(value) == int:
            return Prefab.ConfigValue(int=value, confidential=confidential)
        elif type(value) == float:
            return Prefab.ConfigValue(double=value, confidential=confidential)
        elif type(value) == bool:
            return Prefab.ConfigValue(bool=value, confidential=confidential)
        elif type(value) == list:
            return Prefab.ConfigValue(
                string_list=Prefab.StringList(values=[str(x) for x in value]),
                confidential=confidential,
            )
        else:
            return Prefab.ConfigValue(string=str(value), confidential=confidential)

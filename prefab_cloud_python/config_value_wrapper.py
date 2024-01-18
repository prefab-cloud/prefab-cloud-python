import prefab_pb2 as Prefab


class ConfigValueWrapper:
    @staticmethod
    def wrap(value, confidential=None):
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
            return Prefab.ConfigValue(string=value, confidential=confidential)

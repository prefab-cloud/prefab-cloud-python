MAPPING = {int: 1, str: 2, float: 4, bool: 5, list: 10}


class ContextShape:
    def field_type_number(value):
        return MAPPING.setdefault(type(value), MAPPING[str])

class InvalidContextFormatException(Exception):
    "Raised when a provided context is neither a NamedContext nor a dict"

    def __init__(self, context):
        super().__init__("Expected a NamedContext or dict, received a", str(type(context)))


class Context:
    def __init__(self, context={}):
        self.contexts = {}

        if isinstance(context, NamedContext):
            self.contexts[context.name] = context
        elif isinstance(context, dict):
            for (name, values) in context.items():
                if isinstance(values, dict):
                    self.contexts[str(name)] = NamedContext(name, values)
                else:
                    print("Prefab contexts should be a dict with a key of the context name and a value of a dict of the context")
                    self.contexts[""] = self.contexts.get("") or NamedContext("", {})
                    self.contexts[""].merge({name: values})

        else:
            raise InvalidContextFormatException(context)


class NamedContext:
    def __init__(self, name, data={}):
        self.name = str(name)
        self.data = data

    def get(self, key):
        return self.data.get(key)

    def merge(self, other={}):
        for (key, value) in other.items():
            self.data[str(key)] = self.data.get(str(key)) or value

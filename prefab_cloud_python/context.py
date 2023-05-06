from threading import current_thread


class InvalidContextFormatException(Exception):
    "Raised when a provided context is neither a NamedContext nor a dict"

    def __init__(self, context):
        super().__init__(
            "Expected a NamedContext or dict, received a", str(type(context))
        )


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
                    print(
                        "Prefab contexts should be a dict with a key of the context name and a value of a dict of the context"
                    )
                    self.contexts[""] = self.contexts.get("") or NamedContext("", {})
                    self.contexts[""].merge({name: values})

        else:
            raise InvalidContextFormatException(context)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        self.contexts[str(key)] = NamedContext(key, value)

    def get(self, property_key):
        name_and_key = property_key.split(".", maxsplit=1)

        if len(name_and_key) == 1:
            name = ""
            key = property_key
        else:
            name, key = name_and_key

        if self.contexts.get(name):
            return self.contexts[name].get(key)

    def merge(self, key, value):
        original = self.contexts.get(key) or NamedContext(key, data={})
        original.merge(value)
        self.contexts[str(key)] = original

    def clear(self):
        self.contexts = {}

    def to_dict(self):
        d = {}
        for (name, named_context) in self.contexts.items():
            d[name] = named_context.to_dict()
        return d

    def scope(context):
        if not isinstance(context, Context):
            context = Context(context)
        return ScopedContext(context)

    def set_current(context):
        current_thread().prefab_context = context

    def get_current():
        if (
            "prefab_context" not in dir(current_thread())
            or current_thread().prefab_context is None
        ):
            Context.set_current(Context())
        return current_thread().prefab_context

    def merge_with_current(new_context_attributes):
        return Context(Context.get_current().to_dict() | new_context_attributes)


class NamedContext:
    def __init__(self, name, data={}):
        self.name = str(name)
        self.data = data

    def get(self, key):
        return self.data.get(key)

    def merge(self, other={}):
        for (key, value) in other.items():
            self.data[str(key)] = self.data.get(str(key)) or value

    def to_dict(self):
        return self.data


class ScopedContext(object):
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        self.old_context = Context.get_current()
        Context.set_current(self.context)

    def __exit__(self, *args):
        Context.set_current(self.old_context)

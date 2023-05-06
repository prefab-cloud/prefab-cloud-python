from .context import Context

class FeatureFlagClient:
    def __init__(self, base_client):
        self.base_client = base_client

    def feature_is_on(self, feature_name):
        return self.feature_is_on_for(feature_name, None)

    def feature_is_on_for(self, feature_name, lookup_key=None, attributes={}, context=Context.get_current()):
        variant = self.base_client.config_client().get(
            feature_name, False, attributes, lookup_key, context=context
        )

        return self.is_on(variant)

    def get(self, feature_name, lookup_key=None, attributes={}, default=False, context=Context.get_current()):
        value = self._get(feature_name, lookup_key, attributes, context)
        if value is None:
            return default
        return value

    def _get(self, feature_name, lookup_key=None, attributes={}, context=Context.get_current()):
        return self.base_client.config_client().get(
            feature_name, None, attributes, lookup_key, context=context
        )

    def is_on(self, variant):
        try:
            if variant is None:
                return False
            if isinstance(variant, bool):
                return variant
            return variant.bool
        except Exception:
            self.base_client.logger().info(
                f"is_on methods only work for boolean feature flag variants. This feature flag's variant is '{variant}'. Returning False"
            )
            return False

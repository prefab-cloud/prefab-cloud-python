class FeatureFlagClient:
    def __init__(self, base_client):
        self.base_client = base_client

    def feature_is_on(self, feature_name):
        return self.feature_is_on_for(feature_name, None)

    def feature_is_on_for(self, feature_name, lookup_key, attributes={}):
        variant = self.base_client.config_client().get(feature_name, False, attributes, lookup_key)

        return self.is_on(variant)

    def get(self, feature_name, lookup_key=None, attributes={}, default=False):
        value = self._get(feature_name, lookup_key, attributes)
        if value is None:
            return default
        return value

    def _get(self, feature_name, lookup_key=None, attributes={}):
        return self.base_client.config_client().get(feature_name, None, attributes, lookup_key)

    def is_on(self, variant):
        try:
            if variant is None:
                return False
            if isinstance(variant, bool):
                return variant
            return variant.bool
        except:
            self.base_client.logger().info(f"is_on methods only work for boolean feature flag variants. This feature flag's variant is '{variant}'. Returning False")
            return False






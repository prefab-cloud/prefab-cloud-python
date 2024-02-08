import logging
from .context import Context

logger = logging.getLogger(__name__)


class FeatureFlagClient:
    def __init__(self, base_client):
        self.base_client = base_client

    def feature_is_on(self, feature_name, context=Context.get_current()):
        return self.feature_is_on_for(feature_name, context)

    def feature_is_on_for(self, feature_name, context=Context.get_current()):
        variant = self.base_client.config_client().get(
            feature_name, False, context=context
        )
        return self.is_on(variant)

    def get(self, feature_name, default=False, context=Context.get_current()):
        value = self._get(feature_name, context)
        if value is None:
            return default
        return value

    def _get(self, feature_name, context=Context.get_current()):
        return self.base_client.config_client().get(feature_name, None, context=context)

    def is_on(self, variant):
        try:
            if variant is None:
                return False
            if isinstance(variant, bool):
                return variant
            return variant.bool
        except Exception:
            logger.info(
                f"is_on methods only work for boolean feature flag variants. This feature flag's variant is '{variant}'. Returning False",
            )
            return False

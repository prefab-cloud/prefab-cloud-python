from __future__ import annotations
import functools
from typing import Dict, Callable

from .read_write_lock import ReadWriteLock
from .config_value_unwrapper import ConfigValueUnwrapper
from .context import Context
from ._internal_logging import InternalLogger
from .simple_criterion_evaluators import NumericOperators, StringOperators, DateOperators
import prefab_pb2 as Prefab
import google

logger = InternalLogger(__name__)


class ConfigResolver:
    def __init__(self, base_client, config_loader):
        self.local_store = None
        self.lock = ReadWriteLock()
        self.base_client = base_client
        self.config_loader = config_loader
        self.project_env_id = 0
        self.default_context = {}
        self.make_local()

    def get(self, key, context=None) -> "Evaluation | None":
        with self.lock.read_locked():
            raw_config = self.raw(key)

        if raw_config is None:
            merged_context = self.evaluation_context(context)
            return Evaluation(
                config=None,
                value=None,
                config_row_index=0,
                value_index=0,
                context=merged_context,
                resolver=self,
            )
        else:
            return self.evaluate(raw_config, context=context)

    def raw(self, key) -> Prefab.ConfigValue | None:
        via_key = self.local_store.get(key)
        if via_key is not None:
            return via_key["config"]
        return None

    def evaluate(self, config, context=None) -> "Evaluation | None":
        return CriteriaEvaluator(
            config,
            project_env_id=self.project_env_id,
            resolver=self,
            base_client=self.base_client,
        ).evaluate(self.evaluation_context(context))

    def evaluation_context(self, context):
        merged_context = Context()
        merged_context.merge_context_dict(self.base_client.global_context.to_dict())
        merged_context.merge_context_dict(self.default_context)
        if Context.get_current():
            merged_context.merge_context_dict(Context.get_current().to_dict())
        if context:
            merged_context.merge_context_dict(
                Context.normalize_context_arg(context).to_dict()
            )
        return merged_context

    def update(self):
        self.make_local()

    def make_local(self):
        with self.lock.write_locked():
            self.local_store = self.config_loader.calc_config()

    @property
    def default_context(self):
        return self._default_context

    @default_context.setter
    def default_context(self, value):
        self._default_context = Context.normalize_context_arg(value).to_dict()


OPS = Prefab.Criterion.CriterionOperator


class CriteriaEvaluator:
    def __init__(self, config, project_env_id, resolver, base_client):
        self.config = config
        self.project_env_id = project_env_id
        self.resolver = resolver
        self.base_client = base_client

    def evaluate(self, props):
        matching_env_row_values = self.matching_environment_row_values()
        default_row_index = 1 if matching_env_row_values else 0
        for value_index, conditional_value in enumerate(matching_env_row_values):
            if self.all_criteria_match(conditional_value, props):
                return Evaluation(
                    self.config,
                    conditional_value.value,
                    value_index,
                    0,
                    props,
                    self.resolver,
                )
        for value_index, conditional_value in enumerate(self.default_row_values()):
            if self.all_criteria_match(conditional_value, props):
                return Evaluation(
                    self.config,
                    conditional_value.value,
                    value_index,
                    default_row_index,
                    props,
                    self.resolver,
                )
        return None

    def all_criteria_match(self, conditional_value, props):
        for criterion in conditional_value.criteria:
            if not self.evaluate_criterion(criterion, props):
                return False
        return True

    def evaluate_criterion(self, criterion, properties):
        value_from_properties = properties.get(criterion.property_name)
        unwrapped_criterion_value = ConfigValueUnwrapper.deepest_value(
            criterion.value_to_match, self.config, properties
        ).unwrap()

        if criterion.operator in [OPS.LOOKUP_KEY_IN, OPS.PROP_IS_ONE_OF]:
            return self.one_of(criterion, value_from_properties, properties)
        if criterion.operator in [OPS.LOOKUP_KEY_NOT_IN, OPS.PROP_IS_NOT_ONE_OF]:
            return not self.one_of(criterion, value_from_properties, properties)
        if criterion.operator == OPS.IN_SEG:
            return self.in_segment(criterion, properties)
        if criterion.operator == OPS.NOT_IN_SEG:
            return not self.in_segment(criterion, properties)
        if criterion.operator in StringOperators.SUPPORTED_OPERATORS:
            return StringOperators.evaluate(criterion.operator, unwrapped_criterion_value, value_from_properties)
        if criterion.operator == OPS.HIERARCHICAL_MATCH:
            return value_from_properties.startswith(criterion.value_to_match.string)
        if criterion.operator == OPS.ALWAYS_TRUE:
            return True
        if criterion.operator in DateOperators.SUPPORTED_OPERATORS:
            return DateOperators.evaluate(criterion.operator, unwrapped_criterion_value, value_from_properties)
        if criterion.operator in NumericOperators.SUPPORTED_OPERATORS:
            return NumericOperators.evaluate(criterion.operator, unwrapped_criterion_value, value_from_properties)
        if criterion.operator in [OPS.PROP_MATCHES, OPS.PROP_NOT_MATCHES]:
            return self.matches(criterion, value_from_properties, properties)

        if criterion.operator in [OPS.PROP_SEMVER_LESS_THAN, OPS.PROP_SEMVER_EQUAL, OPS.PROP_SEMVER_GREATER_THAN]:
            return self.semver_comparison(criterion, value_from_properties)

        logger.info(f"Unknown criterion operator {criterion.operator}")
        return False

    @staticmethod
    def negate(negate, value):
        return not value if negate else value


    def matches(self, criterion, value_from_properties, properties):
        return False

    def one_of(self, criterion, value, properties):
        criterion_value_or_values = ConfigValueUnwrapper.deepest_value(
            criterion.value_to_match, self.config, properties
        ).unwrap()
        if isinstance(
            criterion_value_or_values, google._upb._message.RepeatedScalarContainer
        ) or isinstance(criterion_value_or_values, list):
            return str(value) in criterion_value_or_values
        return value == criterion_value_or_values

    def in_segment(self, criterion, properties):
        return (
            self.resolver.get(criterion.value_to_match.string, context=properties)
            .raw_config_value()
            .bool
        )

    def matching_environment_row_values(self):
        env_rows = [
            row for row in self.config.rows if row.project_env_id == self.project_env_id
        ]
        if env_rows == []:
            return []
        else:
            return env_rows[0].values

    def default_row_values(self):
        env_rows = [
            row for row in self.config.rows if row.project_env_id != self.project_env_id
        ]
        if env_rows == []:
            return []
        else:
            return env_rows[0].values


    def semver_comparison(self, criterion, value_from_properties):
        return False

    def date_comparison(self, criterion, value_from_properties):
        return False

    @staticmethod
    def compare_to(a, b):
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0


class Evaluation:
    def __init__(
        self,
        config: Prefab.Config | None,
        value: Prefab.ConfigValue | None,
        value_index: int,
        config_row_index: int,
        context: Context,
        resolver: ConfigResolver,
    ):
        self.config = config
        self.value = value
        self.value_index = value_index
        self.config_row_index = config_row_index
        self.context = context
        self.resolver = resolver

    def unwrapped_value(self):
        return self.deepest_value().unwrap()

    def raw_config_value(self):
        return self.value

    @functools.cache
    def deepest_value(self):
        return ConfigValueUnwrapper.deepest_value(
            self.value, self.config, self.resolver, self.context
        )

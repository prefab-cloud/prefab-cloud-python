from .config_value_unwrapper import ConfigValueUnwrapper
import prefab_pb2 as Prefab
import google

OPS = Prefab.Criterion.CriterionOperator


class CriteriaEvaluator:
    def __init__(self, config, project_env_id, resolver, base_client):
        self.config = config
        self.project_env_id = project_env_id
        self.resolver = resolver
        self.base_client = base_client

    def evaluate(self, props):
        for conditional_value in self.matching_environment_row_values():
            if self.all_criteria_match(conditional_value, props):
                return conditional_value.value
        for conditional_value in self.default_row_values():
            if self.all_criteria_match(conditional_value, props):
                return conditional_value.value
        return None

    def all_criteria_match(self, conditional_value, props):
        for criterion in conditional_value.criteria:
            if not self.evaluate_criterion(criterion, props):
                return False
        return True

    def evaluate_criterion(self, criterion, properties):
        if criterion.property_name == "NAMESPACE":
            value_from_properties = self.base_client.options.namespace
        else:
            value_from_properties = properties.get(criterion.property_name)

        if criterion.operator in [OPS.LOOKUP_KEY_IN, OPS.PROP_IS_ONE_OF]:
            return self.matches(criterion, value_from_properties, properties)
        if criterion.operator in [OPS.LOOKUP_KEY_NOT_IN, OPS.PROP_IS_NOT_ONE_OF]:
            return not self.matches(criterion, value_from_properties, properties)
        if criterion.operator == OPS.IN_SEG:
            return self.in_segment(criterion, properties)
        if criterion.operator == OPS.NOT_IN_SEG:
            return not self.in_segment(criterion, properties)
        if criterion.operator == OPS.PROP_ENDS_WITH_ONE_OF:
            if value_from_properties is None:
                return False
            return any(
                [
                    str(value_from_properties).endswith(ending)
                    for ending in criterion.value_to_match.string_list.values
                ]
            )
        if criterion.operator == OPS.PROP_DOES_NOT_END_WITH_ONE_OF:
            if value_from_properties is None:
                return True
            return not any(
                [
                    str(value_from_properties).endswith(ending)
                    for ending in criterion.value_to_match.string_list.values
                ]
            )
        if criterion.operator == OPS.HIERARCHICAL_MATCH:
            return value_from_properties.startswith(criterion.value_to_match.string)
        if criterion.operator == OPS.ALWAYS_TRUE:
            return True

        self.base_client.logger().info(
            f"Unknown criterion operator {criterion.operator}"
        )
        return False

    def matches(self, criterion, value, properties):
        criterion_value_or_values = ConfigValueUnwrapper.unwrap(
            criterion.value_to_match, self.config.key, properties
        )
        if isinstance(
            criterion_value_or_values, google._upb._message.RepeatedScalarContainer
        ):
            return str(value) in criterion_value_or_values
        return value == criterion_value_or_values

    def in_segment(self, criterion, properties):
        return self.resolver.get(
            criterion.value_to_match.string, context=properties
        ).bool

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

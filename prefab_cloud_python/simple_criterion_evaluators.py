from typing import Callable, Mapping, FrozenSet
import prefab_pb2 as Prefab
from types import MappingProxyType
from numbers import Real  # includes both int and float


def negate(negate, value):
    return not value if negate else value


class NumericOperators:
    """Handles numeric comparisons for criterion evaluation."""

    _COMPARE_TO_EVAL: Mapping[Prefab.Criterion.CriterionOperator, Callable[[int], bool]] = MappingProxyType({
        Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN: lambda v: v > 0,
        Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN_OR_EQUAL: lambda v: v >= 0,
        Prefab.Criterion.CriterionOperator.PROP_LESS_THAN: lambda v: v < 0,
        Prefab.Criterion.CriterionOperator.PROP_LESS_THAN_OR_EQUAL: lambda v: v <= 0
    })

    SUPPORTED_OPERATORS: FrozenSet[Prefab.Criterion.CriterionOperator] = frozenset(_COMPARE_TO_EVAL.keys())

    @staticmethod
    def evaluate(
            context_value: Real,
            operator: Prefab.Criterion.CriterionOperator,
            criterion_value: Real
    ) -> bool:
        """
        Evaluates a numeric comparison between two values.

        Args:
            context_value: The value from context
            operator: The comparison operator to apply
            criterion_value: The value from the criterion

        Returns:
            True if the comparison succeeds, False otherwise
        """
        if not (isinstance(criterion_value, Real) and isinstance(context_value, Real)):
            return False

        comparison_result = NumericOperators._compare(context_value, criterion_value)
        return NumericOperators._COMPARE_TO_EVAL[operator](comparison_result)

    @staticmethod
    def _compare(a: Real, b: Real) -> int:
        """Compare two numbers, returning -1, 0, or 1."""
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0




class StringOperators:
    """Handles string comparisons for criterion evaluation."""

    # Group operators by their base operation
    _CONTAINS_OPERATORS = {
        Prefab.Criterion.CriterionOperator.PROP_CONTAINS_ONE_OF,
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_CONTAIN_ONE_OF
    }

    _STARTS_WITH_OPERATORS = {
        Prefab.Criterion.CriterionOperator.PROP_STARTS_WITH_ONE_OF,
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_START_WITH_ONE_OF
    }

    _ENDS_WITH_OPERATORS = {
        Prefab.Criterion.CriterionOperator.PROP_ENDS_WITH_ONE_OF,
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_END_WITH_ONE_OF
    }

    SUPPORTED_OPERATORS: FrozenSet[Prefab.Criterion.CriterionOperator] = frozenset(
        _CONTAINS_OPERATORS | _STARTS_WITH_OPERATORS | _ENDS_WITH_OPERATORS
    )

    _NEGATIVE_OPERATORS: FrozenSet[Prefab.Criterion.CriterionOperator] = frozenset({
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_CONTAIN_ONE_OF,
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_START_WITH_ONE_OF,
        Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_END_WITH_ONE_OF
    })

    _STRING_OPERATIONS = MappingProxyType({
                                              op: lambda s, x: x in s
                                              for op in _CONTAINS_OPERATORS
                                          } | {
                                              op: str.startswith
                                              for op in _STARTS_WITH_OPERATORS
                                          } | {
                                              op: str.endswith
                                              for op in _ENDS_WITH_OPERATORS
                                          })

    @staticmethod
    def evaluate(
            context_value: str,
            operator: Prefab.Criterion.CriterionOperator,
            criterion_value: list[str]
    ) -> bool:
        if not (isinstance(context_value, str) and isinstance(criterion_value, list)):
            return False

        operation = StringOperators._STRING_OPERATIONS[operator]
        negative = operator in StringOperators._NEGATIVE_OPERATORS

        return negate(
            negative,
            any(
                operation(str(context_value), test_value)
                for test_value in criterion_value
            )
        )
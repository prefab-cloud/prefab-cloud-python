from collections import namedtuple
import pytest
import prefab_pb2 as Prefab
from prefab_cloud_python.simple_criterion_evaluators import NumericOperators, StringOperators


class TestNumericComparisons:
    NumberTestCase = namedtuple(
        "NumericComparisonTestCase",  # Kept your original name
        ["description", "contextValue", "operator", "criterionValue", "expectedMatchResult"]
    )

    @pytest.mark.parametrize("case", [
        NumberTestCase(
            "2 is greater than 1",
            2.1,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN,
            1.1,
            True
        ),
        NumberTestCase(
            "2 is not greater than 2",
            2,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN,
            2,
            False
        ),
        NumberTestCase(
            "1 is not greater than 2",
            1,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN,
            2,
            False
        ),
        NumberTestCase(
            "2 is greater than or equal to 1",
            2.1,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN_OR_EQUAL,
            1.1,
            True
        ),
        NumberTestCase(
            "2 is greater than or equal to 2",
            2,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN_OR_EQUAL,
            2,
            True
        ),
        NumberTestCase(
            "1 is not greater than or equal to 2",
            1,
            Prefab.Criterion.CriterionOperator.PROP_GREATER_THAN_OR_EQUAL,
            2,
            False
        ),  #
        NumberTestCase(
            "1.1 is less than 2",
            1.1,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN,
            2,
            True
        ),
        NumberTestCase(
            "2 is not less than 2",
            2,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN,
            2,
            False
        ),
        NumberTestCase(
            "2 is not less than 2",
            2,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN,
            1,
            False
        ),
        NumberTestCase(
            "1.1 is less than or equal to 2",
            1.1,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN_OR_EQUAL,
            2,
            True
        ),
        NumberTestCase(
            "2 is less than or equal to 2",
            2,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN_OR_EQUAL,
            2,
            True
        ),
        NumberTestCase(
            "2 is not less than or equal to 1",
            2,
            Prefab.Criterion.CriterionOperator.PROP_LESS_THAN_OR_EQUAL,
            1,
            False
        ),

    ], ids=lambda c: c.description)
    def test_operator(self, case: NumberTestCase) -> None:
        result = NumericOperators.evaluate(
            case.contextValue,
            case.operator,
            case.criterionValue
        )
        assert result == case.expectedMatchResult

class TestStringOperations:
    StringTestCase = namedtuple(
        "StringComparisonTestCase",  # Kept your original name
        ["description", "contextValue", "operator", "criterionValue", "expectedMatchResult"]
    )

    @pytest.mark.parametrize("case", [
        StringTestCase(
            "foobar starts with foo is true",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_STARTS_WITH_ONE_OF,
            ["foo", "abc"],
            True
        ),
        StringTestCase(
            "foobar does not start with foo is false",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_START_WITH_ONE_OF,
            ["foo", "abc"],
            False
        ),
        StringTestCase(
            "foobar ends with bar is true",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_ENDS_WITH_ONE_OF,
            ["abc", "bar"],
            True
        ),
        StringTestCase(
            "foobar does not end with bar is false",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_END_WITH_ONE_OF,
            ["abc", "bar"],
            False
        ),
        StringTestCase(
            "foobar contains oo is true",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_CONTAINS_ONE_OF,
            ["oo", "abc"],
            True
        ),
        StringTestCase(
            "foobar does not contain oo is false",
            "foobar",
            Prefab.Criterion.CriterionOperator.PROP_DOES_NOT_CONTAIN_ONE_OF,
            ["oo", "abc"],
            False
        ),
    ], ids=lambda c: c.description)
    def test_operator(self, case: StringTestCase) -> None:
        result = StringOperators.evaluate(
            case.contextValue,
            case.operator,
            case.criterionValue)
        assert result == case.expectedMatchResult


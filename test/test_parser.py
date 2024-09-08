import re
import pytest

from src.parser import (
    WildcardExpression,
    NumericExpression,
    StepExpression,
    RangeExpression,
    CommaExpression,
    parse_expression,
    parse_sub_expression,
)


class TestWildcardExpression:
    subject = WildcardExpression

    def test_is_match_matches(self):
        is_match = self.subject.is_match("*")
        assert is_match is True

    @pytest.mark.parametrize("expression", ["A", "1", "/", "-"])
    def test_is_match_not_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is False

    @pytest.mark.parametrize(
        "params",
        [  #
            {"options": [1, 2, 3], "step": 1, "expected": [1, 2, 3]},
            {"options": [1, 2, 3], "step": 2, "expected": [1, 3]},
            {"options": [1, 2, 3], "step": 3, "expected": [1]},
        ],
    )
    def test_expand(self, params):
        options, step, expected = params.values()

        result = self.subject.expand("*", options=options, step=step)
        assert result == expected


class TestNumericExpression:
    subject = NumericExpression

    @pytest.mark.parametrize("expression", ["1", "1 ", " 1 ", " 1"])
    def test_is_match_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is True

    @pytest.mark.parametrize("expression", ["A", "*", "-"])
    def test_is_match_not_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is False

    @pytest.mark.parametrize(
        "params",
        [  #
            {"expression": "1", "expected": [1]},
            {"expression": "-1111", "expected": [1]},
            {"expression": "1111", "expected": [3]},
            {"expression": " 1 ", "expected": [1]},
        ],
    )
    def test_expand(self, params):
        expression, expected = params.values()

        result = self.subject.expand(expression, options=[1, 2, 3])
        assert result == expected


class TestStepExpression:
    subject = StepExpression

    @pytest.mark.parametrize("expression", ["1/2", "*/2"])
    def test_is_match_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is True

    @pytest.mark.parametrize("expression", ["A", "*", "-"])
    def test_is_match_not_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is False

    @pytest.mark.parametrize("expression", ["*/0", "*/Z"])
    def test_rejects_invalid_rhs(self, expression):
        with pytest.raises(
            ValueError,
            match=re.escape(f"expected right-hand-side value in a step expression to be an positive int: {expression}"),
        ):
            self.subject.is_match(expression)

    @pytest.mark.parametrize(
        "params",
        [  #
            {"expression": "*/1", "expected": [1, 2, 3]},
            {"expression": "*/2", "expected": [1, 3]},
            {"expression": "*/3", "expected": [1]},
        ],
    )
    def test_expand(self, params):
        expression, expected = params.values()

        result = parse_sub_expression(expression, options=[1, 2, 3])
        assert result == expected


class TestRangeExpression:
    subject = RangeExpression

    @pytest.mark.parametrize("expression", ["1-2", " 1-2 "])
    def test_is_match_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is True

    @pytest.mark.parametrize("expression", ["A", "*", "1/2"])
    def test_is_match_not_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is False

    @pytest.mark.parametrize("expression", ["1-Z", "Z-1"])
    def test_rejects_non_numeric_rhs_lhs(self, expression):
        with pytest.raises(
            ValueError,
            match=f"expected left-hand-side and right-hand-side value in a range expression to be an int, found: {expression}",
        ):
            self.subject.is_match(expression)

    @pytest.mark.parametrize(
        "params",
        [  #
            {"expression": "1-3", "expected": [1, 2, 3]},
            {"expression": "1-2", "expected": [1, 2]},
            {"expression": "0-5", "expected": [1, 2, 3]},
        ],
    )
    def test_expand(self, params):
        expression, expected = params.values()

        result = parse_sub_expression(expression, options=[1, 2, 3])
        assert result == expected


class TestCommaExpression:
    subject = CommaExpression

    @pytest.mark.parametrize("expression", ["1,2", "*,1-2"])
    def test_is_match_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is True

    @pytest.mark.parametrize("expression", ["A", "*", "1/2"])
    def test_is_match_not_matches(self, expression):
        is_match = self.subject.is_match(expression)
        assert is_match is False

    @pytest.mark.parametrize(
        "params",
        [  #
            {"expression": "1,*", "expected": [1, 2, 3]},
            {"expression": "1, 2, 3", "expected": [1, 2, 3]},
            {"expression": "1,3", "expected": [1, 3]},
        ],
    )
    def test_expand(self, params):
        expression, expected = params.values()

        result = parse_sub_expression(expression, options=[1, 2, 3])
        assert result == expected


ALL_MINUTES = list(range(60))
ALL_HOURS = list(range(24))
ALL_MONTHS = list(range(1, 13))
ALL_DAYS_MONTH = list(range(1, 32))
ALL_DAYS_WEEK = list(range(7))


def skip_every_n(options, n):
    min_value = min(options)
    max_value = max(options)

    return list(range(min_value, max_value + 1, n))


class TestParseExpression:

    @staticmethod
    @pytest.mark.parametrize("expression", ["ABC", f"{'* ' * 4}asdasd", f"{'* ' * 6}asdasd"])
    def test_rejects_malformed_expression(expression):
        with pytest.raises(ValueError, match=re.escape(f"malformed expression: {expression}")):
            parse_expression(expression)

    @staticmethod
    @pytest.mark.parametrize(
        "params",
        [
            # “At every minute.”
            {
                "expression": "* * * * *",
                "expected": {
                    "minute": ALL_MINUTES,
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "At every even minute." | “At every 2nd minute.”
            {
                "expression": "*/2 * * * *",
                "expected": {
                    "minute": skip_every_n(ALL_MINUTES, n=2),
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            #  "At every odd minute." | “At every 2nd minute from 1 through 59.”
            {
                "expression": "1-59/2 * * * *",
                "expected": {
                    "minute": skip_every_n(ALL_MINUTES[1:], n=2),
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # “At every 5th minute.”
            {
                "expression": "*/5 * * * *",
                "expected": {
                    "minute": skip_every_n(ALL_MINUTES, n=5),
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # “At every hour.”
            {
                "expression": "0 * * * *",
                "expected": {
                    "minute": [0],
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # “At every hour at minute 30.”
            {
                "expression": "30 * * * *",
                "expected": {
                    "minute": [30],
                    "hour": ALL_HOURS,
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every two hours" | “At minute 0 past every 2nd hour.”
            {
                "expression": "0 */2 * * *",
                "expected": {
                    "minute": [0],
                    "hour": skip_every_n(ALL_HOURS, n=2),
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every 6th hour" | “At minute 0 past every 6th hour.”
            {
                "expression": "0 */6 * * *",
                "expected": {
                    "minute": [0],
                    "hour": skip_every_n(ALL_HOURS, n=6),
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Between certain hours" | “At minute 0 past every hour from 9 through 17.”
            {
                "expression": "0 9-17 * * *",
                "expected": {
                    "minute": [0],
                    "hour": list(range(9, 17 + 1)),
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Daily" | “At 00:00.”
            {
                "expression": "0 0 * * *",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every Morning" | “At 08:00.”
            {
                "expression": "0 8 * * *",
                "expected": {
                    "minute": [0],
                    "hour": [8],
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every Sunday" | “At 00:00 on Sunday.”
            {
                # "expression": "0 0 * * SUN",
                "expression": "0 0 * * 0",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": [0],
                },
            },
            # "Every weekday" | “At 00:00 on every day-of-week from Monday through Friday.”
            {
                "expression": "0 0 * * 1-5",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": ALL_DAYS_MONTH,
                    "month": ALL_MONTHS,
                    "day_week": list(range(1, 5 + 1)),
                },
            },
            # "Every month"
            {
                "expression": "0 0 1 * *",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": [1],
                    "month": ALL_MONTHS,
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every other month" | “At 00:00 on day-of-month 1 in every 2nd month.”
            {
                "expression": "0 0 1 */2 *",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": [1],
                    "month": skip_every_n(ALL_MONTHS, n=2),
                    "day_week": ALL_DAYS_WEEK,
                },
            },
            # "Every year" | “At 00:00 on day-of-month 1 in January.”
            {
                "expression": "0 0 1 1 *",
                "expected": {
                    "minute": [0],
                    "hour": [0],
                    "day_month": [1],
                    "month": [1],
                    "day_week": ALL_DAYS_WEEK,
                },
            },
        ],
    )
    def test_parse_expression(params):
        expression, expected = params.values()
        result = parse_expression(f"{expression} command")

        assert result == (expected | {"command": "command"})

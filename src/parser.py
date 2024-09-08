import re
from abc import ABC


def get_int_value(string: str, *, min_value: int, max_value: int):
    return max(min(int(string), max_value), min_value)


class BaseExpression(ABC):
    @staticmethod
    def is_match(expression: str) -> bool:
        raise NotImplementedError()

    @staticmethod
    def expand(expression: str, *, options: list[int], step: int = 1):
        raise NotImplementedError()


class WildcardExpression(BaseExpression):
    """Handles "*" expression"""

    @staticmethod
    def is_match(expression: str) -> bool:
        return expression == "*"

    @staticmethod
    def expand(expression: str, *, options: list[int], step: int = 1):
        if step > 1:
            min_value = min(options)
            max_value = max(options)

            return list(range(min_value, max_value + 1, step))
        else:
            return options


class NumericExpression(BaseExpression):
    """Handles "\\d+" expression"""

    DETECTION_PATTERN = r"^(?P<number>\d+)$"

    @classmethod
    def is_match(cls, expression: str) -> bool:
        return bool(re.match(cls.DETECTION_PATTERN, string=expression.strip()))

    @staticmethod
    def expand(expression: str, *, options: list[int], step: int = 1):
        min_value = min(options)
        max_value = max(options)

        return [get_int_value(expression, min_value=min_value, max_value=max_value)]


class StepExpression(BaseExpression):
    """Handles "{expr} / \\d+" expression"""

    DETECTION_PATTERN = r"^(.*)/([1-9]\d*)$"
    ERROR_MESSAGES = {
        "invalid_rhs": "expected right-hand-side value in a step expression to be an positive int: {expression}",
    }

    @classmethod
    def is_match(cls, expression: str) -> bool:
        if "/" in expression:
            if not re.match(cls.DETECTION_PATTERN, string=expression.strip()):
                raise ValueError(cls.ERROR_MESSAGES["invalid_rhs"].format(expression=expression))
            return True
        else:
            return False

    @classmethod
    def expand(cls, expression: str, *, options: list[int], step: int = 1):
        lhs, rhs = expression.split("/")
        rhs_value = int(rhs)
        return parse_sub_expression(lhs, options=options, step=rhs_value)


class RangeExpression(BaseException):
    """Handles "\\d+ - \\d+" expression"""

    DETECTION_PATTERN = r"^(\d+)-(\d+)$"
    ERROR_MESSAGES = {
        "non_numeric": "expected left-hand-side and right-hand-side value in a range expression to be an int, found: {expression}",
    }

    @classmethod
    def is_match(cls, expression: str) -> bool:
        if "-" in expression:
            if not re.match(cls.DETECTION_PATTERN, string=expression.strip()):
                raise ValueError(cls.ERROR_MESSAGES["non_numeric"].format(expression=expression))
            return True
        else:
            return False

    @classmethod
    def expand(cls, expression: str, *, options: list[int], step: int = 1):
        min_value = min(options)
        max_value = max(options)

        lhs, rhs = expression.split("-")
        lhs_value = get_int_value(lhs, min_value=min_value, max_value=max_value)
        rhs_value = get_int_value(rhs, min_value=min_value, max_value=max_value)
        return list(range(lhs_value, rhs_value + 1, step))


class CommaExpression(BaseException):
    """Handles "{expr}, {expr}, ..." expression"""

    @staticmethod
    def is_match(expression: str) -> bool:
        return "," in expression

    @staticmethod
    def expand(expression: str, *, options: list[int], step: int = 1):
        merged = set()

        for sub_expr in expression.split(","):
            sub_egression_result = parse_sub_expression(sub_expr.strip(), options=options, step=step)
            merged.update(sub_egression_result)

        return list(sorted(merged))


SUPPORTED_EXPRESSIONS = [
    CommaExpression,
    WildcardExpression,
    NumericExpression,
    StepExpression,
    RangeExpression,
]


def parse_sub_expression(expression: str, *, options: list[int], step: int = 1) -> list[int]:
    for Expression in SUPPORTED_EXPRESSIONS:
        if Expression.is_match(expression):
            return Expression.expand(expression, options=options, step=step)

    raise ValueError(f"unrecognized expression: {expression}")


EXPRESSION_REGEX_PATTERN = (
    r"^(?P<minute>\S+) (?P<hour>\S+) (?P<day_month>\S+) (?P<month>\S+) (?P<day_week>\S+) (?P<command>\S+)$"
)


def parse_expression(expression: str) -> list[int]:
    if not re.match(pattern=EXPRESSION_REGEX_PATTERN, string=expression.strip()):
        raise ValueError(f"malformed expression: {expression}")

    match_dict = re.match(pattern=EXPRESSION_REGEX_PATTERN, string=expression.strip()).groupdict()
    return {
        "minute": parse_sub_expression(match_dict["minute"], options=list(range(60))),
        "hour": parse_sub_expression(match_dict["hour"], options=list(range(24))),
        "day_month": parse_sub_expression(match_dict["day_month"], options=list(range(1, 31 + 1))),
        "month": parse_sub_expression(match_dict["month"], options=list(range(1, 12 + 1))),
        "day_week": parse_sub_expression(match_dict["day_week"], options=list(range(7))),
        "command": match_dict["command"],
    }

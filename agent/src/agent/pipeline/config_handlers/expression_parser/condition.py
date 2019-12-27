"""
Validate condition entered by user and transform it to StreamSets expression language
"""
import re

COMPARISON_FUNCTIONS = ['contains', 'startsWith', 'endsWith', 'matches']
COMPARISON_LITERALS = ['==', '!=']


def count_opened_parenthesis(literal: str) -> int:
    return len(re.findall(r'^\!?(\(+)|$', literal)[0])


def count_closed_parenthesis(literal: str) -> int:
    parenthesis = re.findall(r'\)+$', literal)
    if parenthesis:
        return len(parenthesis[0])
    return 0


def first_operand_enclosed_in_quotes(literal: str) -> bool:
    return bool(re.search(r'^(\![\(]+|[\(]+)?(\".*\"|\'.*\')$', literal))


def last_operand_enclosed_in_quotes(literal: str) -> bool:
    return bool(re.search(r'^(\".*\"|\'.*\')[\)]*$', literal))


def validate_comparison_literal(literal: str) -> bool:
    if literal in COMPARISON_LITERALS + COMPARISON_FUNCTIONS:
        return True
    return False


def split_to_expressions(condition: str) -> list:
    return re.split(r'[ ]+(?=\&\&|\|\|)', condition)


def split_to_literals(expression: str) -> list:
    return re.split(r'[ ]+(\=\=|\!\=|contains|startsWith|endsWith|matches)[ ]+', expression)


def replace_conjunction_operator(literal: str) -> str:
    return re.sub(r'^(\&\&|\|\|)[ ]+', '', literal)


def validate_condition(condition: str) -> bool:
    parentheses_count_total = 0
    expressions = split_to_expressions(condition)
    for expression in expressions:
        literals = split_to_literals(expression)
        if len(literals) != 3:
            raise ConditionException('Wrong format. Example: "property" == "value" && "property2" contains "value"')

        operand = replace_conjunction_operator(literals[0])
        parentheses_count_total += count_opened_parenthesis(operand)
        if not first_operand_enclosed_in_quotes(operand):
            raise ConditionException(f'Unsupported literal {operand}. Operand must be enclosed in quotes')

        if not validate_comparison_literal(literals[1]):
            raise ConditionException(
                f'Unsupported literal {literals[1]}. Please use "==", "!=", "contains", "startsWith", "endsWith", "matches"')

        parentheses_count_total -= count_closed_parenthesis(literals[2])
        if not last_operand_enclosed_in_quotes(literals[2]):
            raise ConditionException(f'Unsupported literal {literals[2]}. Operand must be enclosed in quotes')

    if parentheses_count_total != 0:
        raise ConditionException('Unclosed parentheses. Please check your expression')
    return True


def get_start_quote_idx(literal: str) -> int:
    try:
        return literal.index('"')
    except ValueError:
        return literal.index("'")


def get_end_quote_idx(literal: str) -> int:
    try:
        return literal.rindex('"')
    except ValueError:
        return literal.rindex("'")


def get_expression(condition: str) -> str:
    validate_condition(condition)
    expressions = split_to_expressions(condition)

    condition = []
    for expression in expressions:
        literals = split_to_literals(expression)

        start_quote_idx = get_start_quote_idx(literals[0])
        exp_start = literals[0][:start_quote_idx]
        operand = f"record:value('/{literals[0][start_quote_idx + 1:-1]}')"

        if literals[1] in COMPARISON_LITERALS:
            literals[0] = exp_start + operand
            condition.append(' '.join(literals))
            continue

        end_quote_idx = get_end_quote_idx(literals[2])
        exp_end = literals[2][end_quote_idx + 1:]
        sdc_function = f'str:{literals[1]}({operand}, {literals[2][:end_quote_idx + 1]})'
        condition.append(exp_start + sdc_function + exp_end)

    return ' '.join(condition)


class ConditionException(Exception):
    pass

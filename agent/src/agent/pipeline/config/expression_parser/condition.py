"""
Validate condition entered by user and transform it to StreamSets expression language
"""
import re
import regex

COMPARISON_FUNCTIONS = ['contains', 'startsWith', 'endsWith', 'matches']
COMPARISON_LITERALS = ['==', '!=']
# function name: num of arguments
FUNCTIONS = {
    'str:regExCapture': 3
}


def process_expression(condition: str) -> str:
    validate(condition)
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


def process_value(value: str) -> str:
    value = value.strip()
    if is_function(value):
        validate_function(value)
        return replace_first_argument(value)
    return f"'{value}'"


def count_opened_parenthesis(literal: str) -> int:
    return len(re.findall(r'^\!?(\(+)|$', literal)[0])


def count_closed_parenthesis(literal: str) -> int:
    parenthesis = re.findall(r'\)+$', literal)
    if parenthesis:
        return len(parenthesis[0])
    return 0


def first_operand_enclosed_in_quotes(literal: str) -> bool:
    return bool(re.search(r'^(\![\(]+|[\(]+)?(\".*\"|\'.*\')$', literal))


def last_operand_enclosed_in_quotes_or_null(literal: str) -> bool:
    return literal == 'null' or bool(re.search(r'^(\".*\"|\'.*\')[\)]*$', literal))


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


def validate(condition: str) -> bool:
    parentheses_count_total = 0
    expressions = split_to_expressions(condition)
    for expression in expressions:
        literals = split_to_literals(expression)
        if len(literals) != 3:
            raise ConditionException('Wrong format. Example: "property" == "value" && "property2" contains "value": ' + condition)

        operand = replace_conjunction_operator(literals[0])
        parentheses_count_total += count_opened_parenthesis(operand)
        if not first_operand_enclosed_in_quotes(operand):
            raise ConditionException(f'Unsupported literal {operand}. Operand must be enclosed in quotes')

        if not validate_comparison_literal(literals[1]):
            raise ConditionException(
                f'Unsupported literal {literals[1]}. Please use ' + ', '.join(COMPARISON_FUNCTIONS + COMPARISON_LITERALS))

        parentheses_count_total -= count_closed_parenthesis(literals[2])
        if not last_operand_enclosed_in_quotes_or_null(literals[2]):
            raise ConditionException(f'Unsupported literal {literals[2]}. Operand must be enclosed in quotes')

    if parentheses_count_total != 0:
        raise ConditionException('Unclosed parentheses. Please check your expression')
    return True


def validate_value(value: str):
    if is_function(value):
        validate_function(value)


def validate_function(function: str):
    f_name = _get_function_name(function)
    if not f_name:
        raise ConditionException('Unsupported function, supported functions are: ' + ', '.join(FUNCTIONS.keys()))
    num_of_args = get_number_of_arguments(function)
    if num_of_args != FUNCTIONS[f_name]:
        raise ConditionException(f'Function `{f_name}` takes {FUNCTIONS[f_name]} arguments, {num_of_args} provided')


def _get_function_name(function: str) -> str:
    for f in FUNCTIONS.keys():
        if function.strip().startswith(f):
            return f
    return ''


def get_number_of_arguments(function: str) -> int:
    args = extract_arguments(function)
    if not args:
        return 0
    args = re.split('\s*,\s*', args)
    return len(args)


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


def is_function(expression: str) -> bool:
    res = re.findall('[a-zA-Z0-9:_]+\(.*\)', expression)
    return len(res) > 0 and res[0] == expression


def replace_first_argument(function: str) -> str:
    args = extract_arguments(function)
    comma_ind = args.find(',')
    if comma_ind != -1:
        arg = args[:comma_ind]
    else:
        arg = args
    return re.sub(arg, f'record:value(\'/{arg}\')', function)


def extract_arguments(function: str) -> str:
    return regex.findall(r'\(((?:.*|(?R)))\)', function)[0]


class ConditionException(Exception):
    pass

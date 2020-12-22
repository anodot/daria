import pytest

from agent.pipeline.config import expression_parser


@pytest.mark.parametrize("literal, expected_result", [
    ('"test"', 0),
    ('("test"', 1),
    ('((("test"', 3),
    ('!((("test"', 3),
    ('!!((("test"', 0),
    ('"(test"', 0),
    ('("(test"', 1),
])
def test_count_opened_parenthesis(literal, expected_result):
    assert expression_parser.condition.count_opened_parenthesis(literal) == expected_result


@pytest.mark.parametrize("literal, expected_result", [
    ('"test"', 0),
    ('"test")', 1),
    ('"test")))', 3),
    ('"tes)t")))', 3),
    ('"test)"', 0),
])
def test_count_closed_parenthesis(literal, expected_result):
    assert expression_parser.condition.count_closed_parenthesis(literal) == expected_result


@pytest.mark.parametrize("literal, expected_result", [
    ('"test"', True),
    ("'test'", True),
    ("\"test'", False),
    ("'test\"", False),
    ('"', False),
    ('""', True),
    ('"test', False),
    ('test"', False),
    ('te"st"', False),
    ('"test"))', False),
    ('(("test"', True),
    ('!("test"', True),
    ('!("test', False),
])
def test_first_operand_enclosed_in_quotes(literal, expected_result):
    assert expression_parser.condition.first_operand_enclosed_in_quotes(literal) == expected_result


@pytest.mark.parametrize("literal, expected_result", [
    ('"test"', True),
    ("'test'", True),
    ("\"test'", False),
    ("'test\"", False),
    ('"', False),
    ('""', True),
    ('"test', False),
    ('test"', False),
    ('te"st"', False),
    ('"test"))', True),
    ('(("test"', False),
    ('!("test"', False),
    ('null', True)
])
def test_last_operand_enclosed_in_quotes_or_null(literal, expected_result):
    assert expression_parser.condition.last_operand_enclosed_in_quotes_or_null(literal) == expected_result


@pytest.mark.parametrize("condition, expected_result", [
    ('"prop" == "val" && "prop2" contains "val2"', ['"prop" == "val"', '&& "prop2" contains "val2"']),
    ('"prop" == "val" || "prop2" contains \'val2\'', ['"prop" == "val"', '|| "prop2" contains \'val2\'']),
    ('"prop" == "val" | "prop2" contains "val2"', ['"prop" == "val" | "prop2" contains "val2"']),
    ('"prop" == "val" & "prop2" contains "val2"', ['"prop" == "val" & "prop2" contains "val2"']),
    ('("prop" == "val" && "prop2" contains "val2") || fdggfd', ['("prop" == "val"', '&& "prop2" contains "val2")', '|| fdggfd']),
    ('("prop" == "val" && !("prop2" contains "val2"))', ['("prop" == "val"', '&& !("prop2" contains "val2"))']),
    ('"prop" == "val" wer "sdf"', ['"prop" == "val" wer "sdf"']),
    ('"prop" == "val"   &&', ['"prop" == "val"', '&&']),
])
def test_split_to_expressions(condition, expected_result):
    assert expression_parser.condition.split_to_expressions(condition) == expected_result


@pytest.mark.parametrize("expression, expected_result", [
    ('"prop" == "val"', ['"prop"', '==', '"val"']),
    ('\'prop\' != \'val\'', ['\'prop\'', '!=', '\'val\'']),
    ('"prop" contains "val"', ['"prop"', 'contains', '"val"']),
    ('"prop" matches "val"', ['"prop"', 'matches', '"val"']),
    ('"prop" startsWith "val"', ['"prop"', 'startsWith', '"val"']),
    ('"prop" endsWith "val"', ['"prop"', 'endsWith', '"val"']),
    ('"prop" == "val val val"', ['"prop"', '==', '"val val val"']),
    ('"prop/prop1" == "val"', ['"prop/prop1"', '==', '"val"']),
    ('"prop" smth "val"', ['"prop" smth "val"']),
    ('!("prop"  ==   "val"))', ['!("prop"', '==', '"val"))']),
    ('!("prop"  ==   null))', ['!("prop"', '==', 'null))']),
])
def test_split_to_literals(expression, expected_result):
    assert expression_parser.condition.split_to_literals(expression) == expected_result


@pytest.mark.parametrize("condition, expected_result", [
    ('"prop" == "val" && "prop2" contains "val2"', 'record:value(\'/prop\') == "val" && str:contains(record:value(\'/prop2\'), "val2")'),
    ("'prop' == 'val' || 'prop2' contains 'val2'", 'record:value(\'/prop\') == \'val\' || str:contains(record:value(\'/prop2\'), \'val2\')'),
    ('("prop" == "val" && !("prop2" matches "val2"))', '(record:value(\'/prop\') == "val" && !(str:matches(record:value(\'/prop2\'), "val2")))'),
    ('"prop" != "val"', 'record:value(\'/prop\') != "val"'),
    ('"prop" startsWith "val"', 'str:startsWith(record:value(\'/prop\'), "val")'),
    ('"prop" endsWith "val"', 'str:endsWith(record:value(\'/prop\'), "val")'),
    ('"prop" != null', 'record:value(\'/prop\') != null'),
])
def test_get_filtering_expression(condition, expected_result):
    assert expression_parser.condition.process_expression(condition) == expected_result


@pytest.mark.parametrize("value, expected_result", [
    ('test', '\'test\''),
    ('(some == thing)', '\'(some == thing)\''),
    ('str:regExCapture(test, regex, 3)', 'str:regExCapture(record:value(\'/test\'), regex, 3)'),
])
def test_process_value(value, expected_result):
    assert expression_parser.condition.process_value(value) == expected_result


@pytest.mark.parametrize("value, expected_result", [
    ('test', False),
    ('(test)', False),
    ('test()', True),
    ('sys:testMy_Func()', True),
    ('not a function()', False),
])
def test_is_function(value, expected_result):
    assert expression_parser.condition.is_function(value) == expected_result


@pytest.mark.parametrize("value, expected_result", [
    ('str:myFunc(test)', 'str:myFunc(record:value(\'/test\'))'),
    ('func_tion(testThis)', 'func_tion(record:value(\'/testThis\'))'),
    ('str:myFunc(test, 3)', 'str:myFunc(record:value(\'/test\'), 3)'),
])
def test_replace_first_argument(value, expected_result):
    assert expression_parser.condition.replace_first_argument(value) == expected_result


@pytest.mark.parametrize("value, expected_result", [
    ('str:myFunc("test")', 1),
    ('str:myFunc("test", 2)', 2),
    ('str_myFunc()', 0),
    ('myFunc("test)", "test",10)', 3),
    ("str:regExCapture(value_from_kafka, '(.+)\.(.+)', 1)", 3),
])
def test_get_number_of_arguments(value, expected_result):
    assert expression_parser.condition.get_number_of_arguments(value) == expected_result

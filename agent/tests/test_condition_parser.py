import pytest

from agent.pipeline.config_handlers import condition_parser


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
    assert condition_parser.count_opened_parenthesis(literal) == expected_result


@pytest.mark.parametrize("literal, expected_result", [
    ('"test"', 0),
    ('"test")', 1),
    ('"test")))', 3),
    ('"tes)t")))', 3),
    ('"test)"', 0),
])
def test_count_closed_parenthesis(literal, expected_result):
    assert condition_parser.count_closed_parenthesis(literal) == expected_result


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
    assert condition_parser.first_operand_enclosed_in_quotes(literal) == expected_result


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
    ('!("test"', False)
])
def test_last_operand_enclosed_in_quotes(literal, expected_result):
    assert condition_parser.last_operand_enclosed_in_quotes(literal) == expected_result


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
    assert condition_parser.split_to_expressions(condition) == expected_result


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
])
def test_split_to_literals(expression, expected_result):
    assert condition_parser.split_to_literals(expression) == expected_result


@pytest.mark.parametrize("condition, expected_result", [
    ('"prop" == "val" && "prop2" contains "val2"', 'record:value(\'/prop\') == "val" && str:contains(record:value(\'/prop2\'), "val2")'),
    ("'prop' == 'val' || 'prop2' contains 'val2'", 'record:value(\'/prop\') == \'val\' || str:contains(record:value(\'/prop2\'), \'val2\')'),
    ('("prop" == "val" && !("prop2" matches "val2"))', '(record:value(\'/prop\') == "val" && !(str:matches(record:value(\'/prop2\'), "val2")))'),
    ('"prop" != "val"', 'record:value(\'/prop\') != "val"'),
    ('"prop" startsWith "val"', 'str:startsWith(record:value(\'/prop\'), "val")'),
    ('"prop" endsWith "val"', 'str:endsWith(record:value(\'/prop\'), "val")'),
])
def test_get_filtering_expression(condition, expected_result):
    assert condition_parser.get_expression(condition) == expected_result

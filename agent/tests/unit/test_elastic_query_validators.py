import pytest

from agent.pipeline.prompt import elastic


@pytest.mark.parametrize("query, offset_field, er", [
    ('"sort": [{"timestamp": {"order": "asc"}}],', 'timestamp', True),
    ('"sort":\n   [{"timestamp":\n\n       { "order": "asc" }}],', 'timestamp', True),
    ('"sort": [{"timestamp_unix_ms": {"order": "asc"}}],', 'timestamp', False),
    ('"sort": [{"timestamp": {"order": "asc"}}],', 'bla', False),
    ('"sort": [{"timestamp":\n {"bla": "desc"}}],', 'timestamp', False),
    ('"aort":\n   [{"timestamp":\n\n       { "order": "asc" }}],', 'timestamp', False),
])
def test_timestamp_validation(query, offset_field, er):
    assert elastic.is_valid_timestamp(query, offset_field) == er


@pytest.mark.parametrize("query, er", [
    ('"query": {"range": {"timestamp_unix_ms": {"gt": ${OFFSET}}}}', True),
    ('"query":\n   {\n"range":\n {"timestamp_unix_ms":\n {\n "gt":\n   ${OFFSET}}}}', True),
    ('"query": {"range": {"timestamp_unix_ms": {"gte": ${OFFSET}}}}', False),
    ('"query": {"range": {"timestamp_unix_ms": {"gt": OFFSET}}}', False),
])
def test_offset_validation(query, er):
    assert elastic.is_valid_offset(query) == er

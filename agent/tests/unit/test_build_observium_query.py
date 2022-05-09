from unittest.mock import Mock
from agent import data_extractor
from agent import source


def test_build_observium_query():
    source_ = Mock()
    source_.type = source.TYPE_OBSERVIUM

    pipeline_ = Mock()
    pipeline_.source = source_
    pipeline_.timestamp_path = 'poll_time'
    pipeline_.interval = 300
    pipeline_.query = 'select * from some_table where {TIMESTAMP_CONDITION}'

    ar = data_extractor.observium.observium._build_query(pipeline_, 1649000000)
    er = f'select * from some_table where {pipeline_.timestamp_path} >= {1649000000 - pipeline_.interval} and {pipeline_.timestamp_path} < 1649000000'
    assert ar == er

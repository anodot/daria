import pytest

from ...test_input.test_zpipeline_base import TestInputBase


class TestRawSNMP(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'raw/sources/snmp'}],
        'test_create_raw_with_file': [{'file_name': 'raw/pipelines/snmp'}],
    }

    def test_create_with_file(self, cli_runner, file_name=None, override_config=None):
        pytest.skip()

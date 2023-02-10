import pytest

from ..test_zpipeline_base import TestPipelineBase


class TestElastic(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [ {'name': 'test_es_file_full'},
                       {'name': 'test_es_file_with_schema'}],
        'test_reset': [{'name': 'test_es_file_full'}],
        'test_stop': [{'name': 'test_es_file_full'},
                      {'name': 'test_es_file_with_schema'}],
        'test_output': [{'name': 'test_es_file_full', 'output': 'elastic_no_schema.json',
                         'pipeline_type': 'elastic'},
                        {'name': 'test_es_file_with_schema', 'output': 'elastic_schema.json',
                         'pipeline_type': 'elastic'}],
        'test_delete_pipeline': [{'name': 'test_es_file_full'},
                                 {'name': 'test_es_file_with_schema'}],
        'test_source_delete': [{'name': 'elastic_old'}, {'name': 'test_elastic_1'}],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_output_schema(self, name=None, pipeline_type=None, output=None):
        pytest.skip()

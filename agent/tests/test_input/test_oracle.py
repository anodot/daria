from agent import source, pipeline
from .test_zpipeline_base import TestInputBase


class TestOracle(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'oracle_sources'}],
        'test_create_with_file': [{'file_name': 'jdbc_pipelines_oracle'}],
    }

    def test_source_create(self, cli_runner):
        pass

    def test_create(self, cli_runner):
        pass

    def test_create_advanced(self, cli_runner):
        pass

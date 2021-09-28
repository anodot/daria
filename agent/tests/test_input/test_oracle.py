from agent.modules import constants
from .test_zpipeline_base import TestInputBase


class TestOracle(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'oracle_sources'}],
        'test_create_with_file': [{'file_name': 'jdbc_pipelines_oracle'}],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        constants.VALIDATION_ENABLED = False
        super(TestOracle, self).test_create_source_with_file(cli_runner, file_name)
        constants.VALIDATION_ENABLED = True

    def test_create_with_file(self, cli_runner, file_name, config: dict):
        super(TestOracle, self).test_create_with_file(cli_runner, file_name, config)

    def test_source_create(self, cli_runner, name, type, conn):
        pass

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        pass

    def test_create_advanced(self, cli_runner, name, source):
        pass

    @classmethod
    def teardown_class(cls):
        pass

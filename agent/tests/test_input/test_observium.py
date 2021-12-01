from agent import cli, pipeline
from .test_zpipeline_base import TestInputBase
from agent.tests.conftest import get_input_file_path


# todo we have wrong docs, they say when editing via file all fields are optional, though all fields are required
class TestObservium(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'observium_sources'}],
        'test_create_with_file': [{'file_name': 'observium_pipelines'}],
        'test_edit_with_file': [{'file_name': 'observium_pipelines_edit.json'}],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    def test_edit_with_file(self, cli_runner, file_name):
        result = cli_runner.invoke(cli.pipeline.edit, ['-f', get_input_file_path(file_name)], catch_exceptions=False)
        assert result.exit_code == 0

    def test_schema(self):
        assert pipeline.repository.get_by_id('observium_storage').schema == {
            "version": "1",
            "name": "observium_storage",
            "dimensions": ["Storage_size", "Host_Name", "Location"],
            "measurements": {
                "my_own_field": {"aggregation": "average", "countBy": "none"},
                "storage_perc": {"aggregation": "average", "countBy": "none"},
            },
            "missingDimPolicy": {"action": "fill", "fill": "NULL"}, "id": "observium_storage-1234"
        }

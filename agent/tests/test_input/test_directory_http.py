from agent import pipeline
from .test_zpipeline_base import TestInputBase
from ..test_pipelines.test_zpipeline_base import get_schema_id


class TestDirectory(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'directory/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'directory/pipelines'
        }],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    def test_schema(self):
        pipeline_id = 'test_dir_csv'
        assert pipeline.repository.get_by_id(pipeline_id).schema == {
            'id': get_schema_id(pipeline_id),
            'version': '1',
            'name': pipeline_id,
            'dimensions': ['ver', 'Country', 'Exchange', 'optional_dim', 'version'],
            'measurements': {
                'clicks': {
                    'aggregation': 'average',
                    'countBy': 'none'
                },
                'count_records': {
                    'aggregation': 'sum',
                    'countBy': 'none'
                }
            },
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }

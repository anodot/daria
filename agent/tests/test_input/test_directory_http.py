import os

from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.streamsets_api_client import api_client
from ...pipeline import pipeline_repository
from ...source import source_repository


class TestDirectory:

    params = {}

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input="directory\ntest_dir_csv\n/home/test-directory-collector\n*.csv\nDELIMITED\n\ny\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source_repository.SOURCE_DIRECTORY, 'test_dir_csv.json'))

    def test_create(self, cli_runner):
        pipeline_id = 'test_dir_csv'
        result = cli_runner.invoke(pipeline_cli.create, ['-a'],
                                   input=f"{pipeline_id}\ntest_dir_csv\n\ny\ncount_records\ny\n\nClicks:gauge\nClicks:clicks\ntimestamp_datetime\nstring\nMMddyyyy\nver Country\nExchange optional_dim\nversion:1\n\n\n\n1h\n\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(pipeline_id)
        pipeline = pipeline_repository.get(pipeline_id)
        assert pipeline.config['schema'] == {
            'id': '111111-22222-3333-4444',
            'version': '1',
            'name': pipeline_id,
            'dimensions': ['ver', 'Country', 'Exchange', 'optional_dim', 'version'],
            'measurements': {'clicks': {'aggregation': 'average', 'countBy': 'none'},
                             'count_records': {'aggregation': 'sum', 'countBy': 'none'}},
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }

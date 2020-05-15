import os

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli, load_object as load_pipeline
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestDirectory:

    params = {}

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input="directory\ntest_dir_csv\n/home/test-directory-collector\n*.csv\nDELIMITED\n\ny\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_dir_csv.json'))

    def test_create(self, cli_runner):
        pipeline_id = 'test_dir_csv'
        result = cli_runner.invoke(pipeline_cli.create,
                                   input=f"{pipeline_id}\ntest_dir_csv\n\ny\ncount_records\nClicks:gauge\nClicks:clicks\ntimestamp_datetime\nstring\nMMddyyyy\nver Country\nExchange optional_dim\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(pipeline_id)
        pipeline = load_pipeline(pipeline_id)
        assert pipeline.config['schema'] == {
            'id': '111111-22222-3333-4444',
            'version': '1',
            'name': pipeline_id,
            'dimensions': ['ver', 'Country', 'Exchange', 'optional_dim'],
            'measurements': {'clicks': {'aggregation': 'average', 'countBy': 'none'},
                             'count_records': {'aggregation': 'sum', 'countBy': 'none'}},
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }

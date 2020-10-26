from agent import pipeline, source
from agent import cli
from agent.pipeline import streamsets


class TestDirectory:

    params = {}

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input="directory\ntest_dir_csv\n/home/test-directory-collector\n*.csv\nDELIMITED\n\ny\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists('test_dir_csv')

    def test_create(self, cli_runner):
        pipeline_id = 'test_dir_csv'
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f"{pipeline_id}\ntest_dir_csv\n\ny\ncount_records\ny\n\nClicks:gauge\nClicks:clicks\ntimestamp_datetime\nstring\nMMddyyyy\n\nver Country\nExchange optional_dim\nversion:1\n\n\n\n1h\n\n\n")
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(pipeline_id)
        pipeline_obj = pipeline.repository.get_by_name(pipeline_id)
        assert pipeline_obj.config['schema'] == {
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

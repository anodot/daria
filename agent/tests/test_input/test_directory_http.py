from agent import pipeline, source
from agent import cli
from .test_zpipeline_base import TestInputBase
from ..test_pipelines.test_zpipeline_base import get_schema_id


class TestDirectory(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'directory_sources'}],
        'test_create_with_file': [{'file_name': 'directory_pipelines'}],
    }

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
        pipeline_obj = pipeline.repository.get_by_id(pipeline_id)
        assert pipeline_obj.schema == {
            'id': get_schema_id(pipeline_id),
            'version': '1',
            'name': pipeline_id,
            'dimensions': ['ver', 'Country', 'Exchange', 'optional_dim', 'version'],
            'dvpConfig': {},
            'measurements': {'clicks': {'aggregation': 'average', 'countBy': 'none'},
                             'count_records': {'aggregation': 'sum', 'countBy': 'none'}},
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }

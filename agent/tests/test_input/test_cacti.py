from datetime import datetime
from agent import pipeline, source
from agent import cli
from .zbase import InputBaseTest
from ..conftest import generate_input


def _get_days_to_backfill():
    return (datetime.now() - datetime.fromtimestamp(1619085000).replace(hour=0, minute=0, second=0)).days


class TestCacti(InputBaseTest):
    params = {
        'test_create_source_with_file': [{'file_name': 'cacti_sources'}],
        'test_create_with_file': [{
            'file_name': 'cacti_pipelines',
            'config': {'days_to_backfill': _get_days_to_backfill()}
        }],
    }

    def test_source_archive_create(self, cli_runner):
        source_name = 'cacti_archive'
        input_ = {
            'type': 'cacti',
            'name': source_name,
            'mysql conn': 'mysql://root@mysql:3306/cacti',
            'is archive': 'y',
            'rrd files archive': '/usr/src/app/tests/input_files/cacti_rrd.tar.gz',
            'source cache ttl': 3600,
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(source_name)

    def test_source_dir_create(self, cli_runner):
        source_name = 'cacti_dir'
        input_ = {
            'type': 'cacti',
            'name': source_name,
            'mysql conn': 'mysql://root@mysql:3306/cacti',
            'is archive': 'n',
            'rrd files dir': '/usr/src/app/tests/input_files',
            'source cache ttl': 3600,
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(source_name)

    def test_archive_pipeline_create(self, cli_runner):
        delay = 5
        pipeline_id = 'cacti_archive'
        input_ = {
            'source': 'cacti_archive',
            'id': pipeline_id,
            'step': 300,
            'interval in sec': 3600,
            'collect since': _get_days_to_backfill(),
            'delay': delay,
            'add_graph_name_dimension': 'y',
            'static dims': 'static_dim:cacti',
            'tags': 'tag:cacti',
            'transform file': '/home/cacti_transform.csv',
            'rename dimensions': 'query_ifAlias:alias query_ifName:name',
            'Convert bytes into bits': 'n',
            'preview': 'y',
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        pipeline.repository.get_by_id(pipeline_id)

    def test_dir_pipeline_create(self, cli_runner):
        offset = datetime.fromtimestamp(1619085000).replace(hour=0, minute=0, second=0)
        delay = 5
        pipeline_id = 'cacti_dir'
        input_ = {
            'source': 'cacti_dir',
            'id': pipeline_id,
            'step': 300,
            'interval in sec': 3600,
            'collect since': (datetime.now() - offset).days,
            'delay': delay,
            'add_graph_name_dimension': 'y',
            'static dims': 'static_dim:cacti',
            'tags': 'tag:cacti',
            'transform file': '/home/cacti_transform.csv',
            'rename dimensions': 'query_ifAlias:alias query_ifName:name',
            'Convert bytes into bits': 'y',
            'preview': 'y',
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        pipeline.repository.get_by_id(pipeline_id)

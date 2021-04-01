from datetime import datetime
from agent import pipeline, source
from agent import cli
from .test_zpipeline_base import TestInputBase
from ..conftest import generate_input


class TestCacti(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'cacti_sources'}],
        'test_create_with_file': [{'file_name': 'cacti_pipelines'}],
    }

    def test_source_create(self, cli_runner):
        source_name = 'cacti'
        input_ = {
            'type': 'cacti',
            'name': source_name,
            'mysql conn': 'mysql://root@mysql:3306/cacti',
            'rrd files dir': '/usr/src/app/tests/input_files/cacti_rrd.tar.gz',
            'source cache ttl': 3600,
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(source_name)

    def test_create(self, cli_runner):
        offset = datetime.fromtimestamp(1615808400).replace(hour=0, minute=0, second=0)
        delay = 5
        pipeline_id = 'cacti'
        input_ = {
            'source': 'cacti',
            'id': pipeline_id,
            'step': 300,
            'interval in sec': 3600,
            'collect since': (datetime.now() - offset).days,
            'delay': delay,
            'exclude hosts': '*exclude_me*',
            'exclude sources': '*mee too*',
            'static dims': 'static_dim:cacti',
            'tags': 'tag:cacti',
            'transform file': '/home/cacti_transform.csv',
            'rename dimensions': 'query_ifAlias:alias query_ifName:name',
            'preview': 'y',
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        pipeline.repository.get_by_id(pipeline_id)

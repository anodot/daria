from datetime import datetime
from agent import pipeline, source
from agent import cli
from ..conftest import generate_input


class TestCacti:

    params = {}

    def test_source_create(self, cli_runner):
        source_name = 'cacti'
        input_ = {
            'type': 'cacti',
            'name': source_name,
            'mysql conn': 'mysql://root@mysql:3306/cacti',
            'rrd files dir': '/usr/src/app/tests/input_files',
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(source_name)

    def test_create(self, cli_runner):
        offset = datetime.fromtimestamp(1614988800)
        delay = 5
        pipeline_id = 'cacti'
        input_ = {
            'source': 'cacti',
            'id': pipeline_id,
            'step': 300,
            # take everything in one batch
            'interval in sec': int((datetime.utcnow() - offset).total_seconds()) - delay * 60,
            'collect since': (datetime.utcnow() - offset).days,
            'delay': delay,
            # todo exclude smth for test
            'exclude hosts': '',
            'exclude sources': '',
            'static dims': 'static_dim:cacti',
            'tags': 'tag:cacti',
            'preview': 'y',
        }
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        pipeline.repository.get_by_id(pipeline_id)

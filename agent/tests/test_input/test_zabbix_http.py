import sdc_client

from datetime import datetime
from agent import cli
from agent import source, pipeline
from .test_zpipeline_base import TestInputBase
from ..conftest import generate_input, get_input_file_path
from agent.pipeline import PipelineOffset


class TestZabbix(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'zabbix_sources'}],
        'test_create_with_file': [{'file_name': 'zabbix_pipelines'}],
        'test_edit_advanced': [{'pipeline_id': 'test_zabbix'}, {'pipeline_id': 'test_zabbix_edit_query'}],
    }

    def test_source_create(self, cli_runner):
        name = 'test_zabbix'
        input_ = {
            'type': 'zabbix',
            'name': name,
            'url': 'http://zabbix-web:8080',
            'user': 'Admin',
            'password': 'zabbix',
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner):
        pipeline_id = 'test_zabbix'
        input_ = {
            'source': pipeline_id,
            'name': pipeline_id,
            'query file': 'tests/input_files/zabbix_query.json',
            'days to backfill': 0,
            'query interval': 86400,
            'data preview': 'n',
            'count': 'y',
            'counter name': 'counter',
            'value props': 'value:gauge',
            'measurement names': 'value:what',
            'dimensions': 'host content-provider service-provider key_',
            'delay': 0,
            'tags': 'test_type:zabbix',
            'preview': 'n',
        }
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert sdc_client.exists(pipeline_id)

    def test_create_edit_query(self, cli_runner):
        input_file_path = get_input_file_path('zabbix_pipelines_edit_query.json')
        result = cli_runner.invoke(cli.pipeline.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        pipeline_ = pipeline.repository.get_by_id('test_zabbix_edit_query')
        pipeline_.offset = PipelineOffset(pipeline_.id, '{"version": 2, "offsets": {"": "1611320000_30590"}}')
        sdc_client.update(pipeline_)
        pipeline.repository.save_offset(pipeline_.offset)

    def test_edit_advanced(self, cli_runner, pipeline_id: str):
        days_to_backfill = (datetime.now() - datetime(year=2021, month=1, day=22)).days
        input_ = {
            'query file': 'tests/input_files/zabbix_query_2.json',
            'items batch size': '',
            'histories batch size': 50,
            'days to backfill': days_to_backfill,
            'query interval': '',
            'data preview': 'y',
            'count': '',
            'counter name': '',
            'value props': '',
            'measurement names': '',
            'dimensions': '',
            'delay': '',
            'transform file': '/home/zabbix_transform_value.csv',
            'static props': 'test_type:input',
            'tags': 'test:zabbix',
            'preview': 'y',
        }
        result = cli_runner.invoke(
            cli.pipeline.edit, [pipeline_id, '-a'], catch_exceptions=False, input=generate_input(input_)
        )
        assert result.exit_code == 0
        pipeline_ = pipeline.repository.get_by_id_without_session(pipeline_id)
        assert pipeline_.config['days_to_backfill'] == days_to_backfill

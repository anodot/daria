import pytest
import socket

from agent import cli, streamsets
from .test_zpipeline_base import TestPipelineBase
from agent import pipeline, source


class TestTCPServer(TestPipelineBase):

    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'tcp_sources'}],
        'test_create_with_file': [{'file_name': 'tcp_pipelines'}],
        'test_start': [{'name': 'test_tcp_log'}, {'name': 'test_tcp_json'}, {'name': 'test_tcp_csv'}],
        'test_stop': [{'name': 'test_tcp_log'}, {'name': 'test_tcp_json'}, {'name': 'test_tcp_csv'}],
        'test_output': [
            {'name': 'test_tcp_csv', 'output': 'json_value_property_tags.json', 'pipeline_type': source.TYPE_SPLUNK},
            {'name': 'test_tcp_log', 'output': 'log.json', 'pipeline_type': source.TYPE_SPLUNK},
            {'name': 'test_tcp_json', 'output': 'json_value_property.json', 'pipeline_type': source.TYPE_SPLUNK}
        ],
        'test_delete_pipeline': [{'name': 'test_tcp_log'}, {'name': 'test_tcp_json'}, {'name': 'test_tcp_csv'}],
        'test_source_delete': [{'name': 'test_tcp_log'}, {'name': 'test_tcp_json'}, {'name': 'test_tcp_csv'}],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_edit(self, cli_runner):
        pytest.skip()

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_start(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.start, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline_status_by_id(name) == 'RUNNING'

        # streams data
        pipeline_ = pipeline.repository.get_by_name(name)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # strip http:// and port from the end
        host = pipeline_.streamsets.url[7:-6]
        s.connect((host, int(pipeline_.source.config['conf.ports'][0])))

        data = {'LOG': 'log.txt', 'DELIMITED': 'test.csv', 'JSON': 'test_json_items'}
        with open(f'/home/{data[pipeline_.source.config["conf.dataFormat"]]}', 'r') as f:
            for line in f.readlines():
                s.sendall(f'{line}\n'.encode())
        s.close()

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

import json
import os
import time

from ..conftest import get_output, get_input_file_path
from agent.streamsets import StreamSetsApiClient
from agent import pipeline, source, streamsets, cli


class TestPipelineBase(object):
    __test__ = False

    params = {}

    def test_create_source_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(cli.source.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            sources = json.load(f)
            for source_ in sources:
                assert source.repository.exists(f"{source_['name']}")

    def test_create_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(cli.pipeline.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            for pipeline_config in json.load(f):
                pipeline_ = pipeline.repository.get_by_name(pipeline_config['pipeline_id'])
                api_client = StreamSetsApiClient(pipeline_.streamsets)
                assert api_client.get_pipeline(pipeline_config['pipeline_id'])

    def test_edit_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(cli.pipeline.edit, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0

    def test_start(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.start, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline_status_by_id(name) == 'RUNNING'
        # give pipelines some time to send data
        time.sleep(10)

    def test_info(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.info, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_stop(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.stop, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline_status_by_id(name) in ['STOPPED']

    def test_force_stop(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.force_stop, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_reset(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.reset, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_output(self, name, pipeline_type, output):
        expected_output = get_expected_output(name, output, pipeline_type)
        assert get_output(f'{name}_{pipeline_type}.json') == expected_output

    def test_delete_pipeline(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not pipeline.repository.exists(name)

    def test_source_delete(self, cli_runner, name):
        result = cli_runner.invoke(cli.source.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not source.repository.exists(name)


def get_expected_output(name: str, expected_output_file: str, pipeline_type: str) -> list:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{expected_output_file}')) as f:
        expected_output = json.load(f)
        for item in expected_output:
            item['tags']['pipeline_id'] = [name]
            item['tags']['pipeline_type'] = [pipeline_type]
    return expected_output


def get_schema_id(pipeline_id: str) -> str:
    return f'{pipeline_id}-1234'

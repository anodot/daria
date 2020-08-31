import json
import os
import time

from ..fixtures import get_output, get_input_file_path
from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.streamsets_api_client import api_client
from agent import pipeline, source


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.function.__name__ not in metafunc.cls.params:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist])


class TestPipelineBase(object):
    __test__ = False

    params = {}

    def test_create_source_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(source_cli.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            sources = json.load(f)
            for source_ in sources:
                assert os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, f"{source_['name']}.json"))

    def test_create_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(pipeline_cli.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            pipelines = json.load(f)
            for pipeline_ in pipelines:
                assert api_client.get_pipeline(pipeline_['pipeline_id'])

    def test_edit_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name + '.json')
        result = cli_runner.invoke(pipeline_cli.edit, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0

    def test_start(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.start, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'
        # give pipelines some time to send data
        time.sleep(10)

    def test_info(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.info, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_stop(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.stop, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert api_client.get_pipeline_status(name)['status'] in ['STOPPED']

    def test_force_stop(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.force_stop, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_reset(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.reset, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_output(self, name, pipeline_type, output):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
            expected_output = json.load(f)
            for item in expected_output:
                item['tags']['pipeline_id'] = [name]
                item['tags']['pipeline_type'] = [pipeline_type]
        assert get_output(f'{name}_{pipeline_type}.json') == expected_output

    def test_delete_pipeline(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not pipeline.repository.exists(name)

    def test_source_delete(self, cli_runner, name):
        result = cli_runner.invoke(source_cli.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, f'{name}.json'))

import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination, get_input_file_path
from agent.pipeline import cli as pipeline_cli, Pipeline
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.function.__name__ not in metafunc.cls.params:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
            for funcargs in funcarglist])


class TestPipelineBase(object):
    __test__ = False

    params = {}

    def test_create_source_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name)
        result = cli_runner.invoke(source_cli.create, ['-f', input_file_path])
        assert result.exit_code == 0
        with open(input_file_path, 'r') as f:
            sources = json.load(f)
            for source in sources:
                assert os.path.isfile(os.path.join(Source.DIR, f"{source['name']}.json"))

    def test_create_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name)
        result = cli_runner.invoke(pipeline_cli.create, ['-f', input_file_path])
        assert result.exit_code == 0
        with open(input_file_path, 'r') as f:
            pipelines = json.load(f)
            for pipeline in pipelines:
                assert api_client.get_pipeline(pipeline['pipeline_id'])

    def test_edit_with_file(self, cli_runner, file_name):
        input_file_path = get_input_file_path(file_name)
        result = cli_runner.invoke(pipeline_cli.edit, ['-f', input_file_path])
        assert result.exit_code == 0

    def test_start(self, cli_runner, name):
        replace_destination(name)
        result = cli_runner.invoke(pipeline_cli.start, [name])
        assert result.exit_code == 0
        assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'

    def test_stop(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.stop, [name])
        assert result.exit_code == 0
        assert api_client.get_pipeline_status(name)['status'] in ['STOPPED']

    def test_output(self, name, output):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
            expected_output = json.load(f)
        assert get_output(name) == expected_output

    def test_output_exists(self, name):
        assert get_output(name) is not None

    def test_delete_pipeline(self, cli_runner, name):
        result = cli_runner.invoke(pipeline_cli.delete, [name])
        assert result.exit_code == 0
        assert not Pipeline.exists(name)

    def test_source_delete(self, cli_runner, name):
        result = cli_runner.invoke(source_cli.delete, [name])
        assert result.exit_code == 0
        assert not os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

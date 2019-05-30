import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination, get_input_file_path
from agent.constants import PIPELINES_DIR, SOURCES_DIR, TIMESTAMPS_DIR
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli
from agent.streamsets_api_client import api_client


WAITING_TIME = 5


@pytest.mark.parametrize('name,offset', [
    ('test_influx', ' '),
    ('test_influx_offset', '19/03/2019 12:53')
])
def test_source_create(cli_runner, name, offset):
    result = cli_runner.invoke(source_cli.create, input=f"influx\n{name}\nhttp://influx:8086\ntest\n\n{offset}\n\n")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(SOURCES_DIR, f'{name}.json'))


@pytest.mark.parametrize("name,source,options,value,dimensions", [
    ('test_basic', 'test_influx', [], 'usage_active usage_idle', 'cpu zone host'),
    ('test_basic_offset', 'test_influx_offset', [], 'usage_active usage_idle', 'cpu zone host'),
])
def test_create(cli_runner, name, source, options, value, dimensions):
    result = cli_runner.invoke(pipeline_cli.create,
                               options,
                               input=f'{source}\nhttp\n{name}\ncpu_test\n{value}\n\n{dimensions}\n')
    timestamp_file = os.path.join(TIMESTAMPS_DIR, name, 'timestamp')
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)
    assert os.path.isfile(timestamp_file)


def test_create_with_file(cli_runner):
    input_file_path = get_input_file_path('influx_pipelines')
    result = cli_runner.invoke(pipeline_cli.create, ['-f', input_file_path])
    print(result.output)
    assert result.exit_code == 0
    with open(input_file_path, 'r') as f:
        pipelines = json.load(f)
        for pipeline in pipelines:
            assert api_client.get_pipeline(pipeline['pipeline_id'])


def test_edit_with_file(cli_runner):
    input_file_path = get_input_file_path('influx_pipelines_edit')
    result = cli_runner.invoke(pipeline_cli.edit, ['-f', input_file_path])
    print(result.output)
    assert result.exit_code == 0
    with open(input_file_path, 'r') as f:
        pipelines = json.load(f)
        for pipeline in pipelines:
            assert api_client.get_pipeline(pipeline['pipeline_id'])


@pytest.mark.parametrize("name", [
    'test_basic',
    'test_basic_offset',
    'test_influx_file_short',
    'test_influx_file_full',
])
def test_start(cli_runner, name):
    replace_destination(name)
    result = cli_runner.invoke(pipeline_cli.start, [name])
    assert result.exit_code == 0
    # wait until pipeline starts running
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'


@pytest.mark.parametrize("name", [
    'test_basic',
    'test_basic_offset',
    'test_influx_file_short',
    'test_influx_file_full',
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] in ['STOPPED', 'STOPPING']


@pytest.mark.parametrize("name, output", [
    ('test_basic', 'influx.json'),
    ('test_basic_offset', 'influx_offset.json'),
    ('test_influx_file_short', 'influx.json'),
    ('test_influx_file_full', 'influx_file_full.json'),
])
def test_output(name, output):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
        expected_output = json.load(f)
    assert get_output(name) == expected_output


@pytest.mark.parametrize("name", [
    'test_basic_offset',
    'test_basic',
    'test_influx_file_short',
    'test_influx_file_full',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    timestamp_file = os.path.join(TIMESTAMPS_DIR, name, 'timestamp')
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(PIPELINES_DIR, name + '.json'))
    assert not os.path.isfile(timestamp_file)


@pytest.mark.parametrize('name', [
    'test_influx',
    'test_influx_offset'
])
def test_source_delete(cli_runner, name):
    result = cli_runner.invoke(source_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(SOURCES_DIR, f'{name}.json'))

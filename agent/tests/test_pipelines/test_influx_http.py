import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination
from agent.constants import PIPELINES_DIR, SOURCES_DIR
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli
from agent.streamsets_api_client import api_client


WAITING_TIME = 5


@pytest.mark.parametrize('name,offset', [
    ('test_influx', ''),
    ('test_influx_offset', '19/03/2019 12:53')
])
def test_source_create(cli_runner, name, offset):
    result = cli_runner.invoke(source_cli.create, input=f"influx\n{name}\nhttp://influx:8086\ntest\n\n{offset}\n\n")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(SOURCES_DIR, f'{name}.json'))


@pytest.mark.parametrize("name,source,options,value,dimensions", [
    ('test_basic', 'test_influx', [], 'usage_active usage_idle', 'cpu zone host'),
    ('test_basic_offset', 'test_influx_offset', [], 'usage_active usage_idle', 'cpu zone host'),
    ('test_numeric_dimensions', 'test_influx', [], 'usage_active usage_idle', 'usage_iowait'),
    ('test_string_values', 'test_influx', ['-a'], '2123\nconstant', 'zone host\n \nkey1:val1'),
])
def test_create(cli_runner, name, source, options, value, dimensions):
    result = cli_runner.invoke(pipeline_cli.create,
                               options,
                               input=f'{source}\nhttp\n{name}\ncpu_test\n{value}\n\n{dimensions}\n')
    print(result.output)
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


@pytest.mark.parametrize("options,value", [
    (['test_string_values', '-a'], 'cpu usage_active\ncolumn'),
])
def test_edit(cli_runner, options, value):
    result = cli_runner.invoke(pipeline_cli.edit, options, input=f"""\n{value}\n\n\n\n\n\n""")
    assert result.exit_code == 0


@pytest.mark.parametrize("name", [
    'test_basic',
    'test_basic_offset',
    'test_numeric_dimensions',
    'test_string_values',
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
    'test_numeric_dimensions',
    'test_string_values',
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
])
def test_output(name, output):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
        expected_output = json.load(f)
    assert get_output(name) == expected_output


@pytest.mark.parametrize("name", [
    'test_numeric_dimensions',
    'test_string_values',
])
def test_no_output(name):
    assert get_output(name) is None


@pytest.mark.parametrize("name", [
    'test_basic_offset',
    'test_basic',
    'test_numeric_dimensions',
    'test_string_values',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(PIPELINES_DIR, name + '.json'))


@pytest.mark.parametrize('name', [
    'test_influx',
    'test_influx_offset'
])
def test_source_delete(cli_runner, name):
    result = cli_runner.invoke(source_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(SOURCES_DIR, f'{name}.json'))

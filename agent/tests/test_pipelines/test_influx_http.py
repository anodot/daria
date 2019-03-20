import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli
from agent.streamsets_api_client import api_client


WAITING_TIME = 5


def test_source_create(cli_runner):
    result = cli_runner.invoke(source_cli.create, input=f"influx\ntest_influx\nhttp://influx:8086\ntest\n\n\n\n")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(source_cli.DATA_DIR, f'test_influx.json'))


@pytest.mark.parametrize("name,options,value,dimensions", [
    ('test_basic', [], 'usage_active usage_idle', 'cpu zone host'),
    ('test_numeric_dimensions', [], 'usage_active usage_idle', 'usage_iowait'),
    ('test_string_values', ['-a'], '2123\nconstant', 'zone host\n '),
])
def test_create(cli_runner, name, options, value, dimensions):
    result = cli_runner.invoke(pipeline_cli.create,
                               options,
                               input=f'test_influx\nhttp\n{name}\ncpu_test\n{value}\n\n{dimensions}\n')
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
    'test_numeric_dimensions',
    'test_string_values',
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] in ['STOPPED', 'STOPPING']


def test_output():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'expected_output/influx.json')) as f:
        expected_output = json.load(f)
    assert get_output('test_basic') == expected_output


@pytest.mark.parametrize("name", [
    'test_numeric_dimensions',
    'test_string_values',
])
def test_no_output(name):
    assert get_output(name) is None


@pytest.mark.parametrize("name", [
    'test_basic',
    'test_numeric_dimensions',
    'test_string_values',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(pipeline_cli.DATA_DIR, name + '.json'))


def test_source_delete(cli_runner):
    result = cli_runner.invoke(source_cli.delete, [f'test_influx'])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(source_cli.DATA_DIR, f'test_influx.json'))

import json
import os
import pytest
import time

from agent.pipeline import cli as pipeline_cli
from agent.destination import cli as destination_cli
from agent.source import cli as source_cli
from agent.streamsets_api_client import api_client
from click.testing import CliRunner


@pytest.fixture(scope="session", autouse=True)
def remove_test_pipelines():
    api_client.delete_by_filtering('test_')


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_source_create(cli_runner):
    result = cli_runner.invoke(source_cli.create, input="""mongo\ntest_mongo\nmongodb://mongo:27017\nroot\nroot\nadmin\ntest\nadtech\n\n2015-01-01 00:00:00\n\n\n\n\n""")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(source_cli.DATA_DIR, 'test_mongo.json'))


def test_destination_create(cli_runner):
    result = cli_runner.invoke(destination_cli.create, input='http\ntest_http\ntest\n')
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(destination_cli.DATA_DIR, 'test_http.json'))


@pytest.mark.parametrize("name,value_type,value,timestamp,timestamp_type", [
    ('test_value_const', 'constant', '1', 'timestamp_unix', 'unix'),
    ('test_timestamp_ms', 'column', 'Clicks', 'timestamp_unix_ms', 'unix_ms'),
    ('test_timestamp_string', 'column', 'Clicks', 'timestamp_string', 'string\nM/d/yyyy H:mm:ss'),
    ('test_timestamp_datetime', 'column', 'Clicks', 'timestamp_datetime', 'datetime'),
])
def test_create(cli_runner, name, value_type, value, timestamp, timestamp_type):
    result = cli_runner.invoke(pipeline_cli.create, input=f"""test_mongo\ntest_http\n{name}\nclicks\n{value}\n{value_type}\n\n{timestamp}\n{timestamp_type}\nver Country\nExchange optional_dim\n""")
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


def replace_destination(name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_destination.json')) as f:
        test_destination = json.load(f)
    pipeline = api_client.get_pipeline(name)
    pipeline['stages'][-1] = test_destination
    api_client.update_pipeline(name, pipeline)


@pytest.mark.parametrize("name", [
    'test_value_const',
    'test_timestamp_ms',
    'test_timestamp_string',
    'test_timestamp_datetime',
])
def test_start(cli_runner, name):
    replace_destination(name)
    result = cli_runner.invoke(pipeline_cli.start, [name])
    assert result.exit_code == 0
    # wait until pipeline starts running
    time.sleep(3)
    assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'


@pytest.mark.parametrize("name", [
    'test_value_const',
    'test_timestamp_ms',
    'test_timestamp_string',
    'test_timestamp_datetime',
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(5)
    assert api_client.get_pipeline_status(name)['status'] == 'STOPPED'


@pytest.mark.parametrize("name,expected_output_file", [
    ('test_value_const', 'expected_output_value_const.json'),
    ('test_timestamp_ms', 'expected_output_value_column.json'),
    ('test_timestamp_string', 'expected_output_value_column.json'),
    ('test_timestamp_datetime', 'expected_output_value_column.json'),
])
def test_output(name, expected_output_file):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), expected_output_file)) as f:
        expected_output = json.load(f)
    for filename in os.listdir('/sdc-data/out'):
        if filename.startswith(f'sdc-{name}'):
            with open(os.path.join('/sdc-data/out', filename)) as f:
                actual_output = json.load(f)
                assert actual_output == expected_output
                return
    pytest.fail('No output file found')

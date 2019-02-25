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
    result = cli_runner.invoke(source_cli.create, input="""mongo\ntest_mongo\nmongodb://mongo:27017\nroot\nroot\nadmin\ntest\nadtec\n\n2015-01-01 00:00:00\n\n\n\n\n""")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(source_cli.DATA_DIR, 'test_mongo.json'))


def test_source_edit(cli_runner):
    result = cli_runner.invoke(source_cli.edit, ['test_mongo'], input="""\n\n\n\n\nadtech\n\n\n\n\n\n\n""")
    with open(os.path.join(source_cli.DATA_DIR, 'test_mongo.json'), 'r') as f:
        source = json.load(f)
        assert source['config']['configBean.mongoConfig.collection'] == 'adtech'
    assert result.exit_code == 0


@pytest.mark.parametrize("name,options,value,timestamp,timestamp_type", [
    ('test_value_const', ['-a'], '2\nconstant', 'timestamp_unix', 'unix'),
    ('test_timestamp_ms', [], 'Clicks\ncolumn', 'timestamp_unix_ms', 'unix_ms'),
    ('test_timestamp_datetime', [], 'Clicks', 'timestamp_datetime', 'datetime'),
    ('test_timestamp_id', [], 'Clicks', '_id', 'unix'),
    ('test_timestamp_string', ['-a'], 'Clicks\nconstant', 'timestamp_string', 'string\nM/d/yyyy H:mm:ss'),
])
def test_create(cli_runner, name, options, value, timestamp, timestamp_type):
    result = cli_runner.invoke(pipeline_cli.create, options, input=f"""test_mongo\nhttp\n{name}\nclicks\n{value}\n\n{timestamp}\n{timestamp_type}\nver Country\nExchange optional_dim\n""")
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


@pytest.mark.parametrize("options,value", [
    (['test_value_const'], '1\n\n'),
    (['test_timestamp_string', '-a'], 'Clicks\ncolumn'),
])
def test_edit(cli_runner, options, value):
    result = cli_runner.invoke(pipeline_cli.edit, options, input=f"""\n{value}\n\n\n\n\n\n""")
    assert result.exit_code == 0


@pytest.mark.parametrize("name", [
    'test_value_const',
    'test_timestamp_ms',
    'test_timestamp_string',
    'test_timestamp_datetime',
    'test_timestamp_id',
])
def test_start(cli_runner, name):
    replace_destination(name)
    result = cli_runner.invoke(pipeline_cli.start, [name])
    assert result.exit_code == 0
    # wait until pipeline starts running
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'


@pytest.mark.parametrize("name", [
    'test_value_const',
    'test_timestamp_ms',
    'test_timestamp_string',
    'test_timestamp_datetime',
    'test_timestamp_id'
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] in ['STOPPED', 'STOPPING']


@pytest.mark.parametrize("name,expected_output_file", [
    ('test_value_const', 'expected_output_value_const.json'),
    ('test_timestamp_ms', 'expected_output_value_column.json'),
    ('test_timestamp_string', 'expected_output_value_column.json'),
    ('test_timestamp_datetime', 'expected_output_value_column.json'),
])
def test_output(name, expected_output_file):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), expected_output_file)) as f:
        expected_output = json.load(f)
    assert get_output(name) == expected_output


@pytest.mark.parametrize("name", [
    'test_timestamp_id'
])
def test_output_exists(name):
    assert get_output(name) is not None


@pytest.mark.parametrize("name", [
    'test_value_const',
    'test_timestamp_ms',
    'test_timestamp_string',
    'test_timestamp_datetime',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(pipeline_cli.DATA_DIR, name + '.json'))


def test_source_delete(cli_runner):
    result = cli_runner.invoke(source_cli.delete, ['test_mongo'])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(source_cli.DATA_DIR, 'test_mongo.json'))

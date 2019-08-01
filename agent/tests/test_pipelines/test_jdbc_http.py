import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination, get_input_file_path
from agent.pipeline import cli as pipeline_cli, Pipeline
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client


WAITING_TIME = 5


@pytest.mark.parametrize('name,type, conn', [
    ('test_mysql', 'mysql', 'mysql://root@mysql:3306/test'),
])
def test_source_create(cli_runner, name, type, conn):
    result = cli_runner.invoke(source_cli.create, input=f"{type}\n{name}\n{conn}\n\n\n\n")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))


@pytest.mark.parametrize("name,source,timestamp_type,timestamp_name", [
    ('test_mysql', 'test_mysql', '', 'timestamp_unix'),
    ('test_mysql_timestamp_ms', 'test_mysql', 'unix_ms', 'timestamp_unix_ms'),
    ('test_mysql_timestamp_datetime', 'test_mysql', 'datetime', 'timestamp_datetime'),
])
def test_create(cli_runner, name, source, timestamp_type, timestamp_name):
    result = cli_runner.invoke(pipeline_cli.create,
                               input=f'{source}\n{name}\ntest\n\nClicks:gauge Impressions:gauge\n{timestamp_name}\n{timestamp_type}\nAdSize Country\n\n\n1000\n')
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


@pytest.mark.parametrize("name,source", [
    ('test_mysql_advanced', 'test_mysql'),
])
def test_create_advanced(cli_runner, name, source):
    result = cli_runner.invoke(pipeline_cli.create, ['-a'],
                               input=f'{source}\n{name}\ntest\ny\nClicks:gauge Impressions:gauge\ntimestamp_unix\nunix\nAdSize Country\nkey1:val1 key2:val2\n\n\n1000\nCountry = "USA"\n')
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


def test_create_with_file(cli_runner):
    input_file_path = get_input_file_path('jdbc_pipelines')
    result = cli_runner.invoke(pipeline_cli.create, ['-f', input_file_path])
    assert result.exit_code == 0
    with open(input_file_path, 'r') as f:
        pipelines = json.load(f)
        for pipeline in pipelines:
            assert api_client.get_pipeline(pipeline['pipeline_id'])


@pytest.mark.parametrize("name", [
    'test_mysql',
    'test_mysql_timestamp_ms',
    'test_mysql_timestamp_datetime',
    'test_mysql_advanced',
    'test_mysql_file_short',
    'test_mysql_file_full',
])
def test_start(cli_runner, name):
    replace_destination(name)
    result = cli_runner.invoke(pipeline_cli.start, [name])
    assert result.exit_code == 0
    # wait until pipeline starts running
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'


@pytest.mark.parametrize("name", [
    'test_mysql',
    'test_mysql_timestamp_ms',
    'test_mysql_timestamp_datetime',
    'test_mysql_advanced',
    'test_mysql_file_short',
    'test_mysql_file_full',
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] in ['STOPPED', 'STOPPING']


@pytest.mark.parametrize("name, output", [
    ('test_mysql', 'jdbc.json'),
    ('test_mysql_timestamp_ms', 'jdbc.json'),
    ('test_mysql_timestamp_datetime', 'jdbc.json'),
    ('test_mysql_advanced', 'jdbc_file_full.json'),
    ('test_mysql_file_short', 'jdbc.json'),
    ('test_mysql_file_full', 'jdbc_file_full.json'),
])
def test_output(name, output):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
        expected_output = json.load(f)
    assert get_output(name) == expected_output


@pytest.mark.parametrize('name', [
    'test_mysql',
    'test_mysql_timestamp_ms',
    'test_mysql_timestamp_datetime',
    'test_mysql_advanced',
    'test_mysql_file_short',
    'test_mysql_file_full',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    pipeline_obj = Pipeline(name)
    assert result.exit_code == 0
    assert not pipeline_obj.exists()


@pytest.mark.parametrize('name', [
    'test_mysql',
])
def test_source_delete(cli_runner, name):
    result = cli_runner.invoke(source_cli.delete, [name])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(Source.DIR, f'{name}.json'))

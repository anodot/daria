import json
import os
import pytest
import time

from ..fixtures import cli_runner, get_output, replace_destination, get_input_file_path
from agent.pipeline import cli as pipeline_cli, Pipeline
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client


WAITING_TIME = 5


@pytest.mark.parametrize("name", [
    'test_kfk_value_const',
    'test_kfk_timestamp_ms',
    'test_kfk_timestamp_kafka',
    'test_kfk_timestamp_string',
])
def test_source_create(cli_runner, name):
    result = cli_runner.invoke(source_cli.create, input=f"kafka\nkafka_{name}\nkafka:29092\nstreamsetsDC\n{name}\n\n")
    assert result.exit_code == 0
    assert os.path.isfile(os.path.join(Source.DIR, f'kafka_{name}.json'))


@pytest.mark.parametrize("name,options,value,timestamp,properties", [
    ('test_kfk_timestamp_kafka', [], 'clicks\nClicks\n', 'y', ''),
    ('test_kfk_value_const', ['-a'], 'y\nclicks\n2\nconstant\n', 'n\ntimestamp_unix\nunix', 'key1:val1'),
    ('test_kfk_timestamp_ms', [], 'clicks\nClicks\nproperty\n', 'n\ntimestamp_unix_ms\nunix_ms', ''),
    ('test_kfk_timestamp_string', ['-a'], 'y\nclicks\nClicks\nconstant\n', 'n\ntimestamp_string\nstring\nM/d/yyyy H:mm:ss', 'key1:val1'),
])
def test_create(cli_runner, name, options, value, timestamp, properties):
    result = cli_runner.invoke(pipeline_cli.create, options, input=f"""kafka_{name}\n{name}\n{value}\n{timestamp}\nver Country\nExchange optional_dim\n{properties}\n""")
    assert result.exit_code == 0
    assert api_client.get_pipeline(name)


def test_create_with_file(cli_runner):
    input_file_path = get_input_file_path('kafka_pipelines')
    result = cli_runner.invoke(pipeline_cli.create, ['-f', input_file_path])

    assert result.exit_code == 0
    with open(input_file_path, 'r') as f:
        pipelines = json.load(f)
        for pipeline in pipelines:
            assert api_client.get_pipeline(pipeline['pipeline_id'])


@pytest.mark.parametrize("options,value", [
    (['test_kfk_value_const'], '\n1\n\n'),
    (['test_kfk_timestamp_string', '-a'], 'n\nAdType\nClicks\nproperty\nagg_type'),
])
def test_edit(cli_runner, options, value):
    result = cli_runner.invoke(pipeline_cli.edit, options, input=f"""{value}\n\n\n\n\n\n\n\n""")
    assert result.exit_code == 0


@pytest.mark.parametrize("name", [
    'test_kfk_value_const',
    'test_kfk_timestamp_ms',
    'test_kfk_timestamp_string',
    'test_kfk_timestamp_kafka',
    'test_kfk_kafka_file_short',
    'test_kfk_kafka_file_full'
])
def test_start(cli_runner, name):
    replace_destination(name)
    result = cli_runner.invoke(pipeline_cli.start, [name])
    assert result.exit_code == 0
    # wait until pipeline starts running
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] == 'RUNNING'


@pytest.mark.parametrize("name", [
    'test_kfk_value_const',
    'test_kfk_timestamp_ms',
    'test_kfk_timestamp_string',
    'test_kfk_timestamp_kafka',
    'test_kfk_kafka_file_short',
    'test_kfk_kafka_file_full'
])
def test_stop(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.stop, [name])
    assert result.exit_code == 0
    # wait until pipeline stops
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status(name)['status'] in ['STOPPED', 'STOPPING']


@pytest.mark.parametrize("name,output", [
    ('test_kfk_value_const', 'json_value_const_adv.json'),
    ('test_kfk_timestamp_ms', 'json_value_property.json'),
    ('test_kfk_timestamp_string', 'json_value_property_kafka_adv.json'),
])
def test_output(name, output):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{output}')) as f:
        expected_output = json.load(f)
    assert get_output(name) == expected_output


@pytest.mark.parametrize("name", [
    'test_kfk_value_const',
    'test_kfk_timestamp_ms',
    'test_kfk_timestamp_string',
    'test_kfk_timestamp_kafka',
])
def test_delete_pipeline(cli_runner, name):
    result = cli_runner.invoke(pipeline_cli.delete, [name])
    pipeline_obj = Pipeline(name)
    assert result.exit_code == 0
    assert not pipeline_obj.exists()


@pytest.mark.parametrize("name", [
    'test_kfk_value_const',
    'test_kfk_timestamp_ms',
    'test_kfk_timestamp_string',
    'test_kfk_timestamp_kafka',
])
def test_source_delete(cli_runner, name):
    result = cli_runner.invoke(source_cli.delete, [f'kafka_{name}'])
    assert result.exit_code == 0
    assert not os.path.isfile(os.path.join(Source.DIR, f'kafka_{name}.json'))

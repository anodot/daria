import json
import subprocess
import traceback
import pytest
import csv

from kafka import KafkaProducer
from agent import cli, source, pipeline
from ..test_zpipeline_base import TestInputBase
from ...conftest import get_input_file_path, Order


class TestKafka(TestInputBase):
    __test__ = True
    params = {
        'test_create': [
            {
                'source_name': 'test_kfk',
                'name': 'test_kfk_value_const',
                'options': ['-a'],
                'value': 'y\nclicks\ny\n\n \n ',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n\n\n\n',
            },
            {
                'source_name': 'test_kfk',
                'name': 'test_kfk_timestamp_ms',
                'options': [],
                'value': 'n\nClicks:gauge\nClicks:clicks',
                'timestamp': 'timestamp_unix_ms\nunix_ms',
                'advanced_options': ''
            },
            {
                'source_name': 'test_kfk',
                'name': 'test_kfk_timestamp_string',
                'options': ['-a'],
                'value': 'y\nclicks\ny\n\n \n ',
                'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss\n',
                'advanced_options': 'key1:val1\ntag1:tagval tag2:tagval\n"Country" != ""\n/home/test-datasets/kafka_transform.csv'
            },
            {
                'source_name': 'test_running_counters',
                'name': 'test_kfk_running_counter',
                'options': ['-a'],
                'value': 'n\ny\n\nClicks:running_counter\nClicks:clicks',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n \n \n \n\nn'
            },
            {
                'source_name': 'test_running_counters',
                'name': 'test_kfk_running_counter_static_tt',
                'options': ['-a'],
                'value': 'n\nn\n \nClicks:running_counter\nClicks:metric',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n \n \n \nn'
            },
            {
                'source_name': 'test_running_counters',
                'name': 'test_kfk_running_counter_dynamic_what',
                'options': ['-a'],
                'value': 'n\nn\n\nClicks:agg_type\nClicks:metric',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n \n \n \nn'
            },
            {
                'source_name': 'test_json_arrays',
                'name': 'test_json_arrays',
                'options': ['-a'],
                'value': 'n\ny\nkpis\n\nClicks:gauge\nClicks:clicks',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': ' \n \n \n \n\nn'
            },
            {
                'source_name': 'test_kfk',
                'name': 'test_kafka_timezone',
                'options': ['-a'],
                'value': 'n\ny\n \nClicks:gauge\n ',
                'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss\nEurope/Berlin',
                'advanced_options': '\n\n\n\n\nn'
            },
        ],
        'test_edit': [
            {'options': ['test_kfk_value_const', '-a'], 'value': 'y\nclicks\n\n\n\n'},
            {'options': ['test_kfk_timestamp_string', '-a'], 'value': 'n\nn\n\nClicks:agg_type\nClicks:metric'}
        ],
        'test_create_transform_value': [
            {
                'pipeline_id': 'test_transform_value',
                'transform_file': '/home/test-datasets/kafka_transform_value.csv'
            },
            {
                'pipeline_id': 'test_transform_value_2',
                'transform_file': '/home/test-datasets/kafka_transform_value_2.csv'
            },
        ],
        'test_create_source_with_file': [{'file_name': 'kafka_sources'}],
        'test_create_with_file': [{'file_name': 'kafka_pipelines'}],
    }

    @classmethod
    def setup_class(cls):
        producer = KafkaProducer(bootstrap_servers=['kafka:29092'],
                                 value_serializer=lambda x: ','.join(x).encode('utf-8'), api_version=(2, 0))
        topic = 'test-partitions'
        with open('/home/test-datasets/test_partitions.csv', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for index, messages in enumerate(reader):
                producer.send(topic, messages, partition=int(index > 3))
                producer.flush()

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create(self, cli_runner, source_name, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(
            cli.pipeline.create, options, catch_exceptions=False,
            input=f"{source_name}\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n\n{advanced_options}\n"
        )
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0
        pipeline_ = pipeline.repository.get_by_id(name)
        assert bool(pipeline_.override_source)

    @pytest.mark.order(Order.PIPELINE_EDIT)
    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(cli.pipeline.edit, options, catch_exceptions=False,
                                   input=f"\n{value}\n\n\n\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create_transform_value(self, cli_runner, pipeline_id: str, transform_file: dict):
        input_ = {
            'source name': 'test_kfk',
            'pipeline id': pipeline_id,
            'preview': 'n',
            'count': 'n',
            'static': 'y',
            'value array': ' ',
            'value properties': 'Clicks:gauge',
            'measurement names': 'Clicks:clicks',
            'timestamp': 'timestamp_unix',
            'timestamp type': 'unix',
            'required dimensions': ' ',
            'optional dimensions': 'title subtitle Country',
            'consumer group': '',
            'additional props': ' ',
            'tags': ' ',
            'filter condition': ' ',
            'transformation file': transform_file,
        }
        result = cli_runner.invoke(cli.pipeline.create, ["-a"], catch_exceptions=False, input='\n'.join(input_.values()))
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0

    # I guess it's testing di.init() for cli, cli_runner doesn't run click app, and subprocess runs it
    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_subprocess(self):
        input_file_path = get_input_file_path('kafka_sources_2.json')
        try:
            subprocess.check_output(['agent', 'source', 'create', '-f', input_file_path], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            raise Exception(f'Status: FAIL\nexit code {exc.returncode}\n{exc.output}')
        with open(input_file_path) as f:
            sources = json.load(f)
            for source_ in sources:
                assert source.repository.exists(f"{source_['name']}")

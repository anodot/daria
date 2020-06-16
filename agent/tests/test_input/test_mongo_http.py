import json
import os

from ..fixtures import cli_runner
from agent.pipeline import cli as pipeline_cli
from agent.source import cli as source_cli, Source
from agent.streamsets_api_client import api_client
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestMongo:

    params = {
        'test_create': [{'name': 'test_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n \n ',
                         'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
                        {'name': 'test_timestamp_ms', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'},
                        {'name': 'test_timestamp_datetime', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_datetime\ndatetime', 'advanced_options': '\n\n'},
                        {'name': 'test_timestamp_string', 'options': ['-a'], 'value': 'n\n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss',
                         'advanced_options': 'key1:val1\n\n\n'}],
        'test_edit': [{'options': ['test_value_const'], 'value': 'y\nclicks\n\n'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input="""mongo\ntest_mongo\nmongodb://mongo:27017\nroot\nroot\nadmin\ntest\nadtech\n\n2015-01-02 00:00:00\n\n\n\n""")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(Source.DIR, 'test_mongo.json'))

    def test_source_edit(self, cli_runner):
        result = cli_runner.invoke(source_cli.edit, ['test_mongo'], input="""\n\n\n\n\n\n\n2015-01-01 00:00:00\n\n\n\n""")
        with open(os.path.join(Source.DIR, 'test_mongo.json'), 'r') as f:
            source_dict = json.load(f)
            assert source_dict['config']['configBean.initialOffset'] == '2015-01-01 00:00:00'
        assert result.exit_code == 0

    def test_create(self, cli_runner, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"test_mongo\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n{advanced_options}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

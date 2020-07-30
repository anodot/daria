import os

from ..fixtures import cli_runner
from agent import cli
from agent.streamsets_api_client import api_client
from agent import source
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestKafka:
    params = {
        'test_source_create': [{'name': 'test_kfk'}, {'name': 'test_running_counters'}, {'name': 'test_json_arrays'}],
        'test_create': [
            {
                'source_name': 'test_kfk',
                'name': 'test_kfk_value_const',
                'options': ['-a'],
                'value': 'y\nclicks\ny\n\n \n ',
                'timestamp': 'timestamp_unix\nunix\n',
                'advanced_options': 'key1:val1\n\n\n'
            },
            {
                'source_name': 'test_kfk',
                'name': 'test_timezone',
                'options': ['-a'],
                'value': 'y\nclicks\ny\n\n \n ',
                'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss\nAustralia/Brisbane',
                'advanced_options': 'key1:val1\n\n\n'
            },
        ],
        'test_edit': [
            {'options': ['test_kfk_value_const'], 'value': 'y\nclicks\n\n'},
        ],
    }

    def test_source_create(self, cli_runner, name):
        result = cli_runner.invoke(cli.source.create,
                                   input=f"kafka\n{name}\nkafka:29092\n{name}\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, f'{name}.json'))

    def test_create(self, cli_runner, source_name, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(
            cli.pipeline.create,
            options,
            input=f"{source_name}\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n\n{advanced_options}\n"
        )
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(cli.pipeline.edit, options, input=f"\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

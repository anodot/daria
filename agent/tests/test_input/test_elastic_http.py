import os

from ..fixtures import get_input_file_path
from agent.cli import source_cli, pipeline_cli
from agent.streamsets_api_client import api_client
from agent import source


class TestElastic:

    params = {
        'test_create': [
            {'name': 'test_es_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n\n \n ',
             'timestamp': '_source/timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
            {'name': 'test_es_timestamp_ms', 'options': [], 'value': 'n\n_source/Clicks:gauge\n_source/Clicks:clicks',
             'timestamp': '_source/timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'}],
        'test_edit': [{'options': ['test_es_value_const'], 'value': 'y\nclicks\n\n\n'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create,
                                   input=f"elastic\ntest_es\nhttp://es:9200\ntest\ntimestamp_unix_ms\nnow-1000d\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, 'test_es.json'))

    def test_create(self, cli_runner, name, options, value, timestamp, advanced_options):
        query_file_path = get_input_file_path('elastic_query.json')
        result = cli_runner.invoke(pipeline_cli.create, options,
                                   input=f"test_es\n{name}\n{query_file_path}\n\n{value}\n{timestamp}\n_source/ver _source/Country\n_source/Exchange optional_dim ad_type ADTYPE GEN\n{advanced_options}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, input=f"\n\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

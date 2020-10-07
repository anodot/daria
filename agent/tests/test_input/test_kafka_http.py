from agent import cli
from agent.modules.streamsets_api_client import api_client
from agent import source


class TestKafka:
    params = {
        'test_source_create': [{'name': 'test_kfk'}, {'name': 'test_running_counters'}, {'name': 'test_json_arrays'}],
        'test_create': [
            {
                'source_name': 'test_kfk',
                'name': 'test_kfk_value_const',
                'options': ['-a'],
                'value': 'y\nclicks\ny\n\n \n ',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n\n\n\n'
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
                'advanced_options': 'key1:val1\ntag1:tagval tag2:tagval\n"Country" == "USA"\n/home/kafka_transform.csv'
            },
            {
                'source_name': 'test_running_counters',
                'name': 'test_kfk_running_counter',
                'options': ['-a'],
                'value': 'n\ny\n\nClicks:running_counter\nClicks:clicks',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': 'key1:val1\n \n \n \nn'
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
                'value': 'n\nn\nkpis\nclicks.display,clicks.search\nClicks:gauge\nClicks:metric',
                'timestamp': 'timestamp_unix\nunix',
                'advanced_options': ' \n \n \n \nn'
            },
            {
                'source_name': 'test_kfk',
                'name': 'test_kafka_timezone',
                'options': ['-a'],
                'value': 'n\ny\n \n\n ',
                'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss\nEurope/Berlin',
                'advanced_options': '\n\n\n\nn'
            },
        ],
        'test_edit': [
            {'options': ['test_kfk_value_const', '-a'], 'value': 'y\nclicks\n\n\n\n'},
            {'options': ['test_kfk_timestamp_string', '-a'], 'value': 'n\nn\n\nClicks:agg_type\nClicks:metric'}
        ],
    }

    def test_source_create(self, cli_runner, name):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"kafka\n{name}\nkafka:29092\n{name}\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, source_name, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(
            cli.pipeline.create, options, catch_exceptions=False,
            input=f"{source_name}\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n\n{advanced_options}\n"
        )
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(cli.pipeline.edit, options, catch_exceptions=False,
                                   input=f"\n{value}\n\n\n\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

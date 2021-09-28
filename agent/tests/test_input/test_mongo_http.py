from agent import source, cli
from .zbase import InputBaseTest


class TestMongo(InputBaseTest):
    params = {
        'test_create': [{'name': 'test_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n\n \n ',
                         'timestamp': 'timestamp_unix\nunix', 'advanced_options': 'key1:val1\n\n\n'},
                        {'name': 'test_timestamp_ms', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_unix_ms\nunix_ms', 'advanced_options': '\n\n'},
                        {'name': 'test_timestamp_datetime', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_datetime\ndatetime', 'advanced_options': '\n\n'},
                        {'name': 'test_timestamp_string', 'options': ['-a'], 'value': 'n\n\n\nClicks:gauge\nClicks:clicks',
                         'timestamp': 'timestamp_string\nstring\nM/d/yyyy H:mm:ss',
                         'advanced_options': 'key1:val1\n\n\n'}],
        'test_edit': [{'options': ['-a', 'test_value_const'], 'value': 'y\nclicks\n\n\n\n'}],
        'test_create_with_file': [{'file_name': 'mongo_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'mongo_sources'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input="""mongo\ntest_mongo\nmongodb://mongo:27017\nroot\nroot\nadmin\ntest\nadtech\n\n2015-01-02 00:00:00\n\n\n\n""")
        assert result.exit_code == 0
        assert source.repository.exists('test_mongo')

    def test_source_edit(self, cli_runner):
        result = cli_runner.invoke(cli.source.edit, ['test_mongo'], catch_exceptions=False,
                                   input="""\n\n\n\n\n\n\n2015-01-01 00:00:00\n\n\n\n""")
        source_ = source.repository.get_by_name_without_session('test_mongo')
        assert source_.config['configBean.initialOffset'] == '2015-01-01 00:00:00'
        assert result.exit_code == 0

    def test_create(self, cli_runner, name, options, value, timestamp, advanced_options):
        result = cli_runner.invoke(cli.pipeline.create, options, catch_exceptions=False,
                                   input=f"test_mongo\n{name}\n\n{value}\n{timestamp}\nver Country\nExchange optional_dim ad_type ADTYPE GEN\n{advanced_options}\n")
        assert result.exit_code == 0

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(cli.pipeline.edit, options, catch_exceptions=False,
                                   input=f"\n{value}\n\n\n\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

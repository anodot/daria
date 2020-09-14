from ..conftest import get_input_file_path
from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.modules.streamsets_api_client import api_client
from datetime import datetime
from agent import source


class TestSage:

    params = {
        'test_create': [
            {'name': 'test_sage_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n\n \n ',
             'advanced_options': 'key1:val1\n\n\n'},
            {'name': 'test_sage', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
             'advanced_options': '\n\n'}],
        'test_edit': [{'options': ['test_sage_value_const'], 'value': 'y\nclicks\n\n\n'}],
    }

    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(source_cli.create, catch_exceptions=False,
                                   input=f"sage\ntest_sage\nhttp://sage/api/search\ncorrect_token\n")
        assert result.exit_code == 0
        assert source.repository.exists('test_sage')

    def test_create(self, cli_runner, name, options, value, advanced_options):
        query_file_path = get_input_file_path('sage_query.txt')
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days
        print(days_to_backfill)
        interval = 60*24
        result = cli_runner.invoke(pipeline_cli.create, options, catch_exceptions=False,
                                   input=f"test_sage\n{name}\n{query_file_path}\n\n{interval}\n{days_to_backfill}\n{value}\nver Country Exchange\n{advanced_options}\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(pipeline_cli.edit, options, catch_exceptions=False,
                                   input=f"\n\n\n\n{value}\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

import pytest
from ..test_zpipeline_base import TestInputBase
from ...conftest import get_input_file_path, Order
from datetime import datetime
from agent import source, cli


def _get_days_to_backfill():
    return (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1


class TestSage(TestInputBase):
    __test__ = True
    params = {
        'test_create': [
            {'name': 'test_sage_value_const', 'options': ['-a'], 'value': 'y\nclicksS\ny\n\n \n ',
             'advanced_options': 'key1:val1\n\n\n'},
            {'name': 'test_sage', 'options': [], 'value': 'n\nClicks:gauge\nClicks:clicks',
             'advanced_options': '\n\n'}],
        'test_edit': [{'options': ['-a', 'test_sage_value_const'], 'value': 'y\nclicks\n\n\n\n'}],
        'test_create_source_with_file': [{'file_name': 'sage_sources'}],
        'test_create_with_file': [
            {'file_name': 'sage_pipelines', 'override_config': {'days_to_backfill': _get_days_to_backfill()}},
            {'file_name': 'sage_pipelines_dvp'},
        ]
    }

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"sage\ntest_sage\nhttp://sage/api/search\ncorrect_token\n")
        assert result.exit_code == 0
        assert source.repository.exists('test_sage')

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create(self, cli_runner, name, options, value, advanced_options):
        query_file_path = get_input_file_path('sage_query.txt')
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days
        print(days_to_backfill)
        interval = 60*24
        result = cli_runner.invoke(cli.pipeline.create, options, catch_exceptions=False,
                                   input=f"test_sage\n{name}\n{query_file_path}\n\n{interval}\n{days_to_backfill}\n{value}\nver Country Exchange\n{advanced_options}\n")
        assert result.exit_code == 0

    @pytest.mark.order(Order.PIPELINE_EDIT)
    def test_edit(self, cli_runner, options, value):
        result = cli_runner.invoke(cli.pipeline.edit, options, catch_exceptions=False,
                                   input=f"\n\n\n\n{value}\n\n\n\n\n\n\n\n\n\n\n\n")
        assert result.exit_code == 0

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)

    @pytest.mark.order(Order.PIPELINE_EDIT)
    def test_edit_with_file(self, cli_runner):
        input_file_path = get_input_file_path('sage_pipelines_dvp_edit.json')
        result = cli_runner.invoke(cli.pipeline.edit, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0

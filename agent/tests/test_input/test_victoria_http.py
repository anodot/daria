from datetime import datetime
from agent import cli
from agent import source
from agent.pipeline import streamsets


class TestVictoria:
    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"victoria\ntest_victoria\nhttp://victoriametrics:8428\n\n\n")
        assert result.exit_code == 0
        assert source.repository.exists('test_victoria')

    def test_create(self, cli_runner):
        name = 'test_victoria'
        interval = 10000
        query = f'log_messages_total[{interval}s]'
        days_to_backfill = (datetime.now() - datetime(year=2020, month=7, day=7)).days + 1
        result = cli_runner.invoke(
            cli.pipeline.create, catch_exceptions=False,
            input=f'test_victoria\n{name}\n{query}\n{days_to_backfill}\n{interval}\n\n'
        )
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_create_advanced(self, cli_runner):
        name = 'test_victoria_a'
        interval = 100000
        query = f'rate(log_messages_total2[{interval}s])'
        days_to_backfill = (datetime.now() - datetime(year=2020, month=7, day=7)).days + 1
        result = cli_runner.invoke(
            cli.pipeline.create, ["-a"], catch_exceptions=False,
            input=f'test_victoria\n{name}\n{query}\naggregated_metric\n{days_to_backfill}\n{interval}\n\nstatic:dimension\ntag:value\n'
        )
        assert result.exit_code == 0
        assert streamsets.manager.get_pipeline(name)

    def test_edit(self, cli_runner):
        result = cli_runner.invoke(cli.pipeline.edit, ['test_victoria'], catch_exceptions=False, input=f"\n\n\n\n")
        assert result.exit_code == 0

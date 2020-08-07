import os
from datetime import datetime

from ..fixtures import cli_runner
from agent import cli
from agent.streamsets_api_client import api_client
from agent import source


class TestVictoria:
    def test_source_create(self, cli_runner):
        result = cli_runner.invoke(cli.source.create,
                                   input=f"victoria\ntest_victoria\nhttp://victoriametrics:8428\n\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, 'test_victoria.json'))

    def test_create(self, cli_runner):
        name = 'test_victoria'
        query = '{__name__!=""}'
        days_to_backfill = (datetime.now() - datetime(year=2020, month=7, day=7)).days + 3
        result = cli_runner.invoke(
            cli.pipeline.create,
            input=f'test_victoria\n{name}\n{query}\n{days_to_backfill}\n1209600\n\n'
        )
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_edit(self, cli_runner):
        result = cli_runner.invoke(cli.pipeline.edit, ['test_victoria'], input=f"\n\n\n\n")
        print(result.output)
        assert result.exit_code == 0

from agent import cli


def test_export_sources(cli_runner):
    cli_runner.invoke(cli.source.export, catch_exceptions=False)

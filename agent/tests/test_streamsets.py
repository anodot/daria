from agent import cli, streamsets


def test_streamsets_1(cli_runner):
    url = 'http://dc:18630'
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input=f'{url}\n\n\n')
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0


def test_edit_streamsets(cli_runner):
    url = 'http://dc:18630'
    result = cli_runner.invoke(cli.streamsets.edit, [url], catch_exceptions=False, input=f'{url}\n\n\n')
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0

from agent import cli, streamsets

url = 'http://dc:18630'
input_ = {
        'url': url,
        'username': '',
        'password': '',
        'agent_external_url': '',
    }


def test_streamsets_1(cli_runner):
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input='\n'.join(input_.values()))
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0


def test_edit_streamsets(cli_runner):
    result = cli_runner.invoke(cli.streamsets.edit, [url], catch_exceptions=False, input='\n'.join(input_.values()))
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0

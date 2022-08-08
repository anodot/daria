from agent import cli, streamsets
from .conftest import generate_input

url = 'http://dc:18630'


def test_streamsets_1(cli_runner):
    input_ = {
        'url': url,
        'username': '',
        'password': '',
        'agent_external_url': '',
        'preferred_type': 'directory'
    }
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input=generate_input(input_))
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0


def test_edit_streamsets(cli_runner):
    input_ = {
        'username': '',
        'password': '',
        'agent_external_url': '',
    }
    result = cli_runner.invoke(cli.streamsets.edit, [url], catch_exceptions=False, input=generate_input(input_))
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0

import sdc_client

from agent import cli, streamsets, pipeline

URL = 'http://dc2:18630'


def test_create_streamsets_2(cli_runner):
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input=f'{URL}\n\n\n')
    streamsets.repository.get_by_url(URL)
    assert result.exit_code == 0


def test_delete_streamsets_2(cli_runner):
    result = cli_runner.invoke(cli.streamsets.delete, [URL], catch_exceptions=False)
    assert len(streamsets.repository.get_all()) == 1
    assert result.exit_code == 0


def test_create_streamsets_2_again(cli_runner):
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input=f'{URL}\n\n\n')
    streamsets.repository.get_by_url(URL)
    assert result.exit_code == 0


def test_balance_streamsets(cli_runner):
    result = cli_runner.invoke(cli.streamsets.balance, catch_exceptions=False)
    assert sdc_client.StreamsetsBalancer().is_balanced()
    assert _is_balanced()
    assert result.exit_code == 0


def _is_balanced() -> bool:
    len1 = len(pipeline.repository.get_by_streamsets_url('http://dc:18630'))
    len2 = len(pipeline.repository.get_by_streamsets_url('http://dc2:18630'))
    return abs(len1 - len2) < 2

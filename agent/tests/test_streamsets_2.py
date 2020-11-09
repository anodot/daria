from agent import cli, streamsets, pipeline

URL = 'http://dc2:18630'


def test_create_streamsets_2(cli_runner):
    result = cli_runner.invoke(cli.streamsets.add, catch_exceptions=False, input=f'{URL}\n\n\n')
    streamsets.repository.get_by_url(URL)
    # one pipeline will be moved between streamsets and back when one is deleted
    # and after that test pipeline output will make sure it still exists and it's correct
    streamsets.manager.StreamsetsBalancer().move_from_streamsets(streamsets_id=1)
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
    assert streamsets.manager.StreamsetsBalancer().is_balanced()
    assert _is_balanced()
    assert result.exit_code == 0


def _is_balanced() -> bool:
    len1 = len(pipeline.repository.get_by_streamsets_id(1))
    len2 = len(pipeline.repository.get_by_streamsets_id(3))
    return abs(len1 - len2) < 2

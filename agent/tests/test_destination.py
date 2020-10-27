import pytest

from agent import cli
from agent import destination, pipeline
from agent.pipeline import streamsets


@pytest.fixture(autouse=True)
def host_id(monkeypatch):
    def constant_host_id(length=10):
        return 'ABCDEF'
    monkeypatch.setattr(destination.HttpDestination, 'generate_host_id', constant_host_id)


def test_destination(cli_runner):
    result = cli_runner.invoke(cli.destination, args=['--url=http://wrong-url'], catch_exceptions=False,
                               input='y\nhttp://squid:3128\n\n\nhttp://dummy_destination\ncorrect_token\ncorrect_key\n')
    assert result.exit_code == 0
    assert destination.repository.exists()
    for streamsets_ in streamsets.repository.get_all():
        assert streamsets.manager.get_pipeline_status(f'{pipeline.MONITORING}_{streamsets_.id}') == 'RUNNING'


def test_edit_destination(cli_runner):
    prev_dest = destination.repository.get()
    result = cli_runner.invoke(cli.destination, catch_exceptions=False,
                               input='y\nhttp://squid:3128\n\n\n\ncorrect_token\n')
    print(result.output)
    curr_dest = destination.repository.get()
    assert result.exit_code == 0
    assert curr_dest.host_id == prev_dest.host_id
    for streamsets_ in streamsets.repository.get_all():
        assert streamsets.manager.get_pipeline_status(f'{pipeline.MONITORING}_{streamsets_.id}') == 'RUNNING'


def test_update(cli_runner):
    result = cli_runner.invoke(cli.pipeline.update, catch_exceptions=False)
    assert result.exit_code == 0

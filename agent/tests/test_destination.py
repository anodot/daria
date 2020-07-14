import pytest

from .fixtures import cli_runner
from agent import cli
from agent import destination
from agent.streamsets_api_client import api_client

WAITING_TIME = 3


@pytest.fixture(autouse=True)
def host_id(monkeypatch):
    def constant_host_id(length=10):
        return 'ABCDEF'

    monkeypatch.setattr(destination.HttpDestination, 'generate_host_id', constant_host_id)


def test_destination(cli_runner):
    result = cli_runner.invoke(cli.destination, args=['--url=http://wrong-url'],
                               input='y\nhttp://squid:3128\n\n\nhttp://dummy_destination\ncorrect_token\ncorrect_key\n')
    print(result.output)
    assert result.exit_code == 0
    assert destination.HttpDestination.exists()
    assert api_client.get_pipeline_status('Monitoring')['status'] == 'RUNNING'


def test_edit_destination(cli_runner):
    prev_dest = destination.HttpDestination.get()
    result = cli_runner.invoke(cli.destination, input='y\nhttp://squid:3128\n\n\n\ncorrect_token\n')
    print(result.output)
    curr_dest = destination.HttpDestination.get()
    assert result.exit_code == 0
    assert curr_dest.host_id == prev_dest.host_id
    assert api_client.get_pipeline_status('Monitoring')['status'] == 'RUNNING'


def test_update(cli_runner):
    result = cli_runner.invoke(cli.pipeline.update)
    assert result.exit_code == 0

import time

import pytest

from agent import cli, streamsets, pipeline
from agent.cli.run_test_pipeline import perform_cleanup
from .conftest import generate_input

url = 'http://dc2:18630'


def test_streamsets_1(cli_runner):
    args = ['--url', url, '--preferred-type', 'directory']
    result = cli_runner.invoke(cli.streamsets.add, args=args, catch_exceptions=False)
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


def test_run_pipeline(cli_runner):
    result = cli_runner.invoke(cli.run_test_pipeline, args=['--no-delete'], catch_exceptions=False)
    print(f"run_test_pipeline: {result.exit_code} {result.output}")
    assert pipeline.repository.get_by_streamsets_url(url)
    perform_cleanup()
    assert result.exit_code == 0


def test_delete_streamsets(cli_runner):
    result = cli_runner.invoke(cli.streamsets.delete, [url], catch_exceptions=False)
    with pytest.raises(streamsets.repository.StreamsetsNotExistsException):
        streamsets.repository.get_by_url(url)
    assert result.exit_code == 0

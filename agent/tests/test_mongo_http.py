import pytest

from agent.cli import create as pipeline_create
from agent.source.cli import create as source_create
from agent.destination.cli import create as destination_create
from click.testing import CliRunner


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_source_create(cli_runner):
    result = cli_runner.invoke(source_create, input="""mongo\ntest_mongo\nmongodb://mongo:27017
    \nroot\nroot\nadmin\ntest\nadtech\n\n2015-01-01 00:00:00\n\n\n\n\n""")
    assert result.exit_code == 0


def test_destination_create(cli_runner):
    result = cli_runner.invoke(destination_create, input='http\ntest_http\ntest\n')
    assert result.exit_code == 0


# def test_create(cli_runner):
#     result = cli_runner.invoke(pipeline_create, input='test_mongo\ntest_http\ntest_mongo_http\nclicks\n')
#     assert result.exit_code == 0

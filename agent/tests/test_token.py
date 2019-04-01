import os

from .fixtures import cli_runner
from agent import cli as agent_cli
from agent.pipeline import cli as pipeline_cli


def test_destination(cli_runner):
    result = cli_runner.invoke(agent_cli.destination, input='token\ny\nhttp://squid:3128\n\n\n')
    assert result.exit_code == 0
    assert os.path.isfile(pipeline_cli.DESTINATION_FILE)

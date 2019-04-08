import os

from .fixtures import cli_runner
from agent import cli as agent_cli
from agent.constants import DESTINATION_FILE


def test_destination(cli_runner):
    result = cli_runner.invoke(agent_cli.destination, input='token\ny\nhttp://squid:3128\n\n\n')
    assert result.exit_code == 0
    assert os.path.isfile(DESTINATION_FILE)

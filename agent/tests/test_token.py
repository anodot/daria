import os

from .fixtures import cli_runner
from agent import cli as agent_cli
from agent.pipeline import cli as pipeline_cli


def test_token(cli_runner):
    result = cli_runner.invoke(agent_cli.token, input='token\n')
    assert result.exit_code == 0
    assert os.path.isfile(pipeline_cli.TOKEN_FILE)

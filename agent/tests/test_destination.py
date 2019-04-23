import os
import time

from .fixtures import cli_runner
from agent import cli as agent_cli
from agent.constants import DESTINATION_FILE
from agent.streamsets_api_client import api_client


WAITING_TIME = 3


def test_destination(cli_runner):
    result = cli_runner.invoke(agent_cli.destination, input='token\ny\nhttp://squid:3128\n\n\n')
    assert result.exit_code == 0
    assert os.path.isfile(DESTINATION_FILE)
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status('Monitoring')['status'] == 'RUNNING'

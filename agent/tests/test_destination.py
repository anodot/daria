import json
import os
import time

from .fixtures import cli_runner
from agent import cli as agent_cli
from agent.constants import DESTINATION_FILE
from agent.streamsets_api_client import api_client


WAITING_TIME = 3


def test_destination(cli_runner):
    result = cli_runner.invoke(agent_cli.destination, input='toke\ny\nhttp://squid:312\n\n\n')
    assert result.exit_code == 0
    assert os.path.isfile(DESTINATION_FILE)
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status('Monitoring')['status'] == 'RUNNING'


def test_edit_destination(cli_runner):
    with open(DESTINATION_FILE, 'r') as f:
        prev_dest = json.load(f)
    result = cli_runner.invoke(agent_cli.destination, input='y\ntoken\ny\nhttp://squid:3128\n\n\n')
    with open(DESTINATION_FILE, 'r') as f:
        curr_dest = json.load(f)
    assert result.exit_code == 0
    assert curr_dest['config']['conf.client.proxy.uri'] == 'http://squid:3128'
    assert curr_dest['host_id'] == prev_dest['host_id']
    time.sleep(WAITING_TIME)
    assert api_client.get_pipeline_status('Monitoring')['status'] == 'RUNNING'

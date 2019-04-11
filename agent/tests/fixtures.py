import json
import os
import pytest

from agent.pipeline import cli as pipeline_cli
from agent.streamsets_api_client import api_client
from click.testing import CliRunner


@pytest.fixture(scope="session")
def cli_runner():

    yield CliRunner()

    api_client.delete_by_filtering('test_')

    for filename in os.listdir(pipeline_cli.SDC_DATA_PATH):
        if filename.startswith('error-test_'):
            os.remove(os.path.join(pipeline_cli.SDC_DATA_PATH, filename))
    if os.path.isdir(pipeline_cli.SDC_RESULTS_PATH):
        for filename in os.listdir(pipeline_cli.SDC_RESULTS_PATH):
            if filename.startswith('sdc-test_'):
                os.remove(os.path.join(pipeline_cli.SDC_RESULTS_PATH, filename))

    if os.path.isfile(pipeline_cli.DESTINATION_FILE):
        os.remove(pipeline_cli.DESTINATION_FILE)


def replace_destination(name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines/test_destination.json')) as f:
        test_destination = json.load(f)
    pipeline = api_client.get_pipeline(name)
    test_destination['inputLanes'] = [pipeline['stages'][-2]['outputLanes'][0]]
    pipeline['stages'][-1] = test_destination
    api_client.update_pipeline(name, pipeline)


def get_output(pipeline_name):
    for filename in os.listdir(pipeline_cli.SDC_RESULTS_PATH):
        if filename.startswith(f'sdc-{pipeline_name}'):
            with open(os.path.join(pipeline_cli.SDC_RESULTS_PATH, filename)) as f:
                return json.load(f)

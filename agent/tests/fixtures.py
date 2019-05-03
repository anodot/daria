import json
import os
import pytest

from agent.streamsets_api_client import api_client
from click.testing import CliRunner
from agent.constants import SDC_DATA_PATH, SDC_RESULTS_PATH, DESTINATION_FILE


@pytest.fixture(scope="session")
def cli_runner():

    yield CliRunner()

    api_client.delete_by_filtering('test_')
    if api_client.get_pipelines(text='Monitoring'):
        api_client.stop_pipeline('Monitoring')
        api_client.delete_pipeline('Monitoring')

    for filename in os.listdir(SDC_DATA_PATH):
        if filename.startswith('error-test_'):
            os.remove(os.path.join(SDC_DATA_PATH, filename))
    if os.path.isdir(SDC_RESULTS_PATH):
        for filename in os.listdir(SDC_RESULTS_PATH):
            if filename.startswith('sdc-test_'):
                os.remove(os.path.join(SDC_RESULTS_PATH, filename))

    if os.path.isfile(DESTINATION_FILE):
        os.remove(DESTINATION_FILE)


def replace_destination(name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines/test_destination.json')) as f:
        test_destination = json.load(f)
    pipeline = api_client.get_pipeline(name)
    test_destination['inputLanes'] = [pipeline['stages'][-2]['outputLanes'][0]]
    pipeline['stages'][-1] = test_destination
    api_client.update_pipeline(name, pipeline)


def get_output(pipeline_name):
    for filename in os.listdir(SDC_RESULTS_PATH):
        if filename.startswith(f'sdc-{pipeline_name}-'):
            with open(os.path.join(SDC_RESULTS_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}.json')

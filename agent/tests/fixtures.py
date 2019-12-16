import json
import os
import pytest
import time

from agent.streamsets_api_client import api_client
from click.testing import CliRunner
from agent.constants import SDC_DATA_PATH, SDC_RESULTS_PATH
from agent.destination.http import HttpDestination
from agent.pipeline import load_object, PipelineManager


@pytest.fixture(scope="session")
def cli_runner():

    yield CliRunner()
    #
    # api_client.delete_by_filtering('test_')
    # if api_client.get_pipelines(text='Monitoring'):
    #     api_client.stop_pipeline('Monitoring')
    #     api_client.force_stop_pipeline('Monitoring')
    #     time.sleep(2)
    #     PipelineManager(load_object('Monitoring')).delete()
    #
    # for filename in os.listdir(SDC_DATA_PATH):
    #     if filename.startswith('error-test_'):
    #         os.remove(os.path.join(SDC_DATA_PATH, filename))
    # if os.path.isdir(SDC_RESULTS_PATH):
    #     for filename in os.listdir(SDC_RESULTS_PATH):
    #         if filename.startswith('sdc-test_'):
    #             os.remove(os.path.join(SDC_RESULTS_PATH, filename))
    #
    # if os.path.isfile(HttpDestination.FILE):
    #     os.remove(HttpDestination.FILE)


def replace_destination(name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines/test_destination.json')) as f:
        test_destination = json.load(f)
    pipeline = api_client.get_pipeline(name)
    test_destination['inputLanes'] = [pipeline['stages'][-2]['outputLanes'][0]]
    for key, stage in enumerate(pipeline['stages']):
        if stage['instanceName'] == 'destination':
            test_destination['inputLanes'] = [pipeline['stages'][key-1]['outputLanes'][0]]
            pipeline['stages'][key] = test_destination
    api_client.update_pipeline(name, pipeline)


def get_output(pipeline_name):
    for filename in os.listdir(SDC_RESULTS_PATH):
        if filename.startswith(f'sdc-{pipeline_name}-'):
            with open(os.path.join(SDC_RESULTS_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}.json')

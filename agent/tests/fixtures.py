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


def get_output(pipeline_name, pipeline_type):
    dummy_destination_output_path = '/output'
    for filename in os.listdir(dummy_destination_output_path):
        if filename == pipeline_name + '_' + pipeline_type + '.json':
            with open(os.path.join(dummy_destination_output_path, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}')

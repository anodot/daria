import json
import os
import pytest

from click.testing import CliRunner


DUMMY_DESTINATION_OUTPUT_PATH = '/output'
TEST_DATASETS_PATH = '/home'


@pytest.fixture(scope="session")
def cli_runner():
    yield CliRunner()


def get_output(file_name):
    for filename in os.listdir(DUMMY_DESTINATION_OUTPUT_PATH):
        if filename == file_name:
            with open(os.path.join(DUMMY_DESTINATION_OUTPUT_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}')

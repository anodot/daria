import json
import os
import pytest

from click.testing import CliRunner


@pytest.fixture(scope="session")
def cli_runner():
    yield CliRunner()


def get_output(file_name):
    dummy_destination_output_path = '/output'
    for filename in os.listdir(dummy_destination_output_path):
        if filename == file_name:
            with open(os.path.join(dummy_destination_output_path, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}')

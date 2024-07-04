import json
import os.path
import pytest
import shutil

import sdc_client

from typing import Callable
from ..conftest import get_input_file_path, Order
from agent import source, cli
from agent.modules import constants


class TestInputBase(object):
    __test__ = False
    params = {}

    @pytest.mark.order(Order.SOURCE_CREATE)
    def test_create_source_with_file(self, cli_runner, file_name):
        constants.VALIDATION_ENABLED = False
        input_file_path = get_input_file_path(f'{file_name}.json')
        result = cli_runner.invoke(cli.source.create, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            sources = json.load(f)
            for source_ in sources:
                assert source.repository.exists(f"{source_['name']}")

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create_with_file(self, cli_runner, file_name, override_config: dict):
        self._test_create_with_file(cli_runner, file_name, override_config, cli.pipeline.create)

    def _test_create_with_file(self, cli_runner, file_name, override_config: dict, create_function: Callable):
        input_file_path = get_input_file_path(f'{file_name}.json')
        input_file_path = _replace_config_in_file(input_file_path, override_config)
        result = cli_runner.invoke(create_function, ['-f', input_file_path], catch_exceptions=False)
        assert result.exit_code == 0
        with open(input_file_path) as f:
            for pipeline_config in json.load(f):
                assert sdc_client.exists(pipeline_config['pipeline_id'])


def _replace_config_in_file(input_file_path, override_config: dict):
    if not override_config:
        return input_file_path

    new_path = os.path.join('/tmp', os.path.basename(input_file_path))
    if os.path.exists(new_path):
        os.remove(new_path)
    shutil.copy(input_file_path, new_path)

    with open(input_file_path) as f:
        pipelines = json.load(f)
    for pipeline_config in pipelines:
        for key, val in override_config.items():
            pipeline_config[key] = val

    with open(new_path, 'w') as f:
        json.dump(pipelines, f)
    return new_path

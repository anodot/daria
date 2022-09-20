import json
import os
import time
import sdc_client

from ..conftest import get_output
from agent import pipeline, source, cli
from typing import Callable


class TestPipelineBase(object):
    __test__ = False

    MAX_TIMES_TO_WAIT = 60

    params = {}

    def _wait(self, condition: Callable):
        i = 0
        while i < self.MAX_TIMES_TO_WAIT and not condition():
            time.sleep(2)
            i += 1

    def test_start(self, cli_runner, name: str, sleep: int):
        result = cli_runner.invoke(cli.pipeline.start, [name], catch_exceptions=False)
        assert result.exit_code == 0
        # if not sleep:
        #     sleep = 20
        # time.sleep(sleep)

        pipeline_ = pipeline.repository.get_by_id(name)

        def check_in_streamsets():
            return sdc_client.get_pipeline_status(pipeline_) == pipeline.Pipeline.STATUS_RUNNING

        self._wait(check_in_streamsets)
        assert check_in_streamsets()

        # give pipelines some time to send data
        # at high load there might be lag before status is updated in the db, so checking after some time

        def check_in_db():
            return pipeline.repository.get_by_id_without_session(name).status == pipeline.Pipeline.STATUS_RUNNING

        self._wait(check_in_db)
        assert check_in_db()

    def test_info(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.info, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def _check_output_file(self, file_name):
        if file_name:
            self._wait(lambda: get_output(file_name))
            assert get_output(file_name)

    def test_stop(self, cli_runner, name, check_output_file_name):
        self._check_output_file(check_output_file_name)
        result = cli_runner.invoke(cli.pipeline.stop, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert sdc_client.get_pipeline_status(pipeline.repository.get_by_id(name)) == pipeline.Pipeline.STATUS_STOPPED

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        self._check_output_file(check_output_file_name)
        result = cli_runner.invoke(cli.pipeline.force_stop, [name], catch_exceptions=False)
        assert result.exit_code == 0

    def test_reset(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.reset, [name], catch_exceptions=False)
        assert result.exit_code == 0

    # def test_output(self, name, pipeline_type, output):
    #     expected_output = get_expected_output(name, output, pipeline_type)
    #     assert get_output(f'{name}_{pipeline_type}.json') == expected_output
    #
    def test_output(self, name, pipeline_type, output):
        def compare_output():
            expected_output = get_expected_output(name, output, pipeline_type)
            actual_output = get_output(f'{name}_{pipeline_type}.json')
            return actual_output == expected_output
        self._wait(compare_output)
        assert compare_output()

    # def test_output_schema(self, name, pipeline_type, output):
    #     expected_output = get_expected_schema_output(name, output, pipeline_type)
    #     assert get_output(f'{name}_{pipeline_type}.json') == expected_output
    #
    def test_output_schema(self, name, pipeline_type, output):
        def compare_output():
            expected_output = get_expected_schema_output(name, output, pipeline_type)
            actual_output = get_output(f'{name}_{pipeline_type}.json')
            return actual_output == expected_output
        self._wait(compare_output)
        assert compare_output()

    def test_delete_pipeline(self, cli_runner, name):
        result = cli_runner.invoke(cli.pipeline.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not sdc_client.exists(name)
        assert not pipeline.repository.exists(name)

    def test_source_delete(self, cli_runner, name):
        result = cli_runner.invoke(cli.source.delete, [name], catch_exceptions=False)
        assert result.exit_code == 0
        assert not source.repository.exists(name)


def get_expected_output(pipeline_id: str, expected_output_file: str, pipeline_type: str = None) -> list:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{expected_output_file}')) as f:
        expected_output = json.load(f)
        for item in expected_output:
            if 'tags' in item:
                item['tags']['pipeline_id'] = [pipeline_id]
                item['tags']['pipeline_type'] = [pipeline_type]
    return expected_output


def get_expected_events_output(expected_output_file: str) -> list:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), f'expected_output/{expected_output_file}')) as f:
        return json.load(f)


def get_expected_schema_output(pipeline_id: str, expected_output_file: str, pipeline_type: str) -> list:
    expected_output = get_expected_output(pipeline_id, expected_output_file, pipeline_type)
    if isinstance(expected_output, dict):
        expected_output = [expected_output]
    for record in expected_output:
        record['schemaId'] = get_schema_id(pipeline_id)
    return expected_output


def get_schema_id(pipeline_id: str) -> str:
    return f'{pipeline_id}-1234'


def sort_output(output: list) -> list:
    return sorted(output, key=lambda x: (x['properties']['what'], x['timestamp']))


def sort_output_schema(output: list) -> list:
    return sorted(output, key=lambda x: x['timestamp'])


def drop_key_value(item: dict, key: str):
    new_item = item.copy()
    new_item.pop(key, None)
    return new_item

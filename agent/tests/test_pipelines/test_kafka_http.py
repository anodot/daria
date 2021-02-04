import json
import subprocess
import pytest

from .test_zpipeline_base import TestPipelineBase
from ..conftest import get_input_file_path
from agent import source


class TestKafka(TestPipelineBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'kafka_sources'}],
        'test_create_with_file': [{'file_name': 'kafka_pipelines'}],
        'test_start': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                       {'name': 'test_kfk_timestamp_string'},
                       {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                       {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                       {'name': 'test_kfk_running_counter_dynamic_what'},
                       {'name': 'test_kfk_running_counter_static_tt'},
                       {'name': 'test_transform_value'},
                       {'name': 'test_transform_value_2'},
                       {'name': 'test_kafka_timezone'}],
        'test_info': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_running_counter'}],
        'test_stop': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                      {'name': 'test_kfk_timestamp_string'},
                      {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                      {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                      {'name': 'test_kfk_running_counter_dynamic_what'},
                      {'name': 'test_kfk_running_counter_static_tt'},
                      {'name': 'test_transform_value'},
                      {'name': 'test_transform_value_2'},
                      {'name': 'test_kafka_timezone'}],
        'test_output': [
            {'name': 'test_kfk_timestamp_string', 'output': 'json_value_property_transformations.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_dynamic_what', 'output': 'running_counter_dynamic_what.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_static_tt', 'output': 'running_counter_static_tt.json',
             'pipeline_type': 'kafka'},
        ],
        'test_output_schema': [
            {'name': 'test_kafka_timezone', 'output': 'kafka_timezone.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_value_const', 'output': 'json_value_const_adv_schema.json', 'pipeline_type': 'kafka'},
            {'name': 'test_transform_value', 'output': 'kafka_transform_value.json', 'pipeline_type': 'kafka'},
            {'name': 'test_transform_value_2', 'output': 'kafka_transform_value_2.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_ms', 'output': 'json_value_property_30.json', 'pipeline_type': 'kafka'},
            {'name': 'test_csv', 'output': 'json_value_property_tags_schema.json', 'pipeline_type': 'kafka'},
        ],
        'test_delete_pipeline': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                                 {'name': 'test_kfk_timestamp_string'},
                                 {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                                 {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                                 {'name': 'test_kfk_running_counter_dynamic_what'},
                                 {'name': 'test_kfk_running_counter_static_tt'},
                                 {'name': 'test_transform_value'},
                                 {'name': 'test_transform_value_2'},
                                 {'name': 'test_kafka_timezone'}],
        'test_source_delete': [{'name': 'test_kfk'}],
    }

    def test_create_subprocess(self):
        input_file_path = get_input_file_path('kafka_sources_2.json')
        try:
            subprocess.check_output(['agent', 'source', 'create', '-f', input_file_path], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            raise Exception(f'Status: FAIL\nexit code {exc.returncode}\n{exc.output}')
        with open(input_file_path) as f:
            sources = json.load(f)
            for source_ in sources:
                assert source.repository.exists(f"{source_['name']}")

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

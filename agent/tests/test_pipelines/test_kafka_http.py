import pytest

from ..fixtures import cli_runner
from .test_zpipeline_base import TestPipelineBase, pytest_generate_tests


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
                       {'name': 'test_kfk_running_counter_static_tt'}],
        'test_info': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_running_counter'}],
        'test_stop': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                      {'name': 'test_kfk_timestamp_string'},
                      {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                      {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                      {'name': 'test_kfk_running_counter_dynamic_what'},
                      {'name': 'test_kfk_running_counter_static_tt'}],
        'test_output': [
            {'name': 'test_kfk_value_const', 'output': 'json_value_const_adv.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_ms', 'output': 'json_value_property.json', 'pipeline_type': 'kafka'},
            {'name': 'test_csv', 'output': 'json_value_property_tags.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_string', 'output': 'json_value_property_transformations.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter', 'output': 'running_counter.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_dynamic_what', 'output': 'running_counter_dynamic_what.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_static_tt', 'output': 'running_counter_static_tt.json',
             'pipeline_type': 'kafka'}
        ],
        'test_delete_pipeline': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_timestamp_ms'},
                                 {'name': 'test_kfk_timestamp_string'},
                                 {'name': 'test_kfk_kafka_file_short'}, {'name': 'test_kfk_kafka_file_full'},
                                 {'name': 'test_csv'}, {'name': 'test_kfk_running_counter'},
                                 {'name': 'test_kfk_running_counter_dynamic_what'},
                       {'name': 'test_kfk_running_counter_static_tt'}],
        'test_source_delete': [{'name': 'test_kfk'}],
    }

    def test_edit_with_file(self, cli_runner, file_name=None):
        pytest.skip()

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

    def test_force_stop(self, cli_runner, name=None):
        pytest.skip()

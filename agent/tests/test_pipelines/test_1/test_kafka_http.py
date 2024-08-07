import pytest

from ..test_zpipeline_base import TestPipelineBase


class TestKafka(TestPipelineBase):
    __test__ = True
    params = {
        'test_start': [
            {'name': 'test_kfk_value_const'},
            {'name': 'test_kfk_timestamp_ms'},
            {'name': 'test_kfk_timestamp_string'},
            {'name': 'test_kfk_kafka_file_short'},
            {'name': 'test_kfk_kafka_file_full'},
            {'name': 'test_csv'},
            {'name': 'test_partitions'},
            {'name': 'test_kfk_running_counter'},
            {'name': 'test_kfk_running_counter_dynamic_what'},
            {'name': 'test_kfk_running_counter_static_tt'},
            {'name': 'test_transform_value'},
            {'name': 'test_transform_value_2'},
            {'name': 'test_json_arrays'},
            {'name': 'test_kafka_timezone'}
        ],
        'test_info': [{'name': 'test_kfk_value_const'}, {'name': 'test_kfk_running_counter'}],
        'test_stop': [{'name': 'test_json_arrays'}],
        'test_force_stop': [
            {'name': 'test_kfk_timestamp_ms'},
            {'name': 'test_kfk_value_const'},
            {'name': 'test_kfk_running_counter'},
            {'name': 'test_kfk_running_counter_dynamic_what'},
            {'name': 'test_kfk_running_counter_static_tt'},
            {'name': 'test_kafka_timezone'},
            {'name': 'test_transform_value'},
            {'name': 'test_kfk_kafka_file_short'},
            {'name': 'test_transform_value_2'},
            {'name': 'test_csv'},
            {'name': 'test_partitions'},
            {'name': 'test_kfk_kafka_file_full'},
            {'name': 'test_kfk_timestamp_string'}
        ],
        'test_output': [
            {'name': 'test_kfk_timestamp_string', 'output': 'kafka_json_value_property_transformations.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_dynamic_what', 'output': 'kafka_running_counter_dynamic_what.json',
             'pipeline_type': 'kafka'},
            {'name': 'test_kfk_running_counter_static_tt', 'output': 'kafka_running_counter_static_tt.json',
             'pipeline_type': 'kafka'},
        ],
        'test_output_schema': [
            {'name': 'test_kafka_timezone', 'output': 'kafka_timezone.json', 'pipeline_type': 'kafka'},
            {'name': 'test_json_arrays', 'output': 'kafka_json_arrays.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_value_const', 'output': 'kafka_json_value_const_adv_schema.json', 'pipeline_type': 'kafka'},
            {'name': 'test_transform_value', 'output': 'kafka_transform_value.json', 'pipeline_type': 'kafka'},
            {'name': 'test_transform_value_2', 'output': 'kafka_transform_value_2.json', 'pipeline_type': 'kafka'},
            {'name': 'test_kfk_timestamp_ms', 'output': 'kafka_json_value_property_30.json', 'pipeline_type': 'kafka'},
            {'name': 'test_csv', 'output': 'kafka_json_value_property_tags_schema.json', 'pipeline_type': 'kafka'},
            # TODO: fix this
            # {'name': 'test_partitions', 'output': 'kafka_json_value_property_tags_schema_with_partitions.json', 'pipeline_type': 'kafka'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_json_arrays'},
            {'name': 'test_kfk_timestamp_ms'},
            {'name': 'test_kfk_value_const'},
            {'name': 'test_kfk_running_counter'},
            {'name': 'test_kfk_running_counter_dynamic_what'},
            {'name': 'test_kfk_running_counter_static_tt'},
            {'name': 'test_kafka_timezone'},
            {'name': 'test_transform_value'},
            {'name': 'test_kfk_kafka_file_short'},
            {'name': 'test_transform_value_2'},
            {'name': 'test_csv'},
            {'name': 'test_partitions'},
            {'name': 'test_kfk_kafka_file_full'},
            {'name': 'test_kfk_timestamp_string'}
        ],
        'test_source_delete': [
            {'name': 'test_json_arrays'},
            {'name': 'test_csv'},
            {'name': 'test_kfk'},
            {'name': 'test_running_counters'},
            {'name': 'test-partitions'},
        ],
    }

    def test_reset(self, cli_runner, name=None):
        pytest.skip()

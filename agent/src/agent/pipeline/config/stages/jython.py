from . import base


class ConvertToMetrics30(base.Stage):
    JYTHON_SCRIPT = 'convert_to_metrics_30.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            script = f.read()
        return {
            'stageRequiredFields': self._get_required_fields(),
            'userParams': [
                {'key': 'TIMESTAMP_COLUMN', 'value': self.pipeline.timestamp_path},
                {'key': 'DIMENSIONS', 'value': self.pipeline.dimensions_with_names},
                {'key': 'MEASUREMENTS', 'value': self.pipeline.values_paths_with_names},
                {'key': 'TARGET_TYPES', 'value': self.pipeline.target_types_paths},
                {'key': 'COUNT_RECORDS', 'value': int(self.pipeline.count_records)},
                {'key': 'COUNT_RECORDS_MEASUREMENT_NAME', 'value': self.pipeline.count_records_measurement_name},
                {'key': 'STATIC_WHAT', 'value': int(self.pipeline.static_what)},
                {'key': 'VALUES_ARRAY_PATH', 'value': self.pipeline.values_array_path},
                {'key': 'VALUES_ARRAY_FILTER', 'value': self.pipeline.values_array_filter_metrics},
                {'key': 'INTERVAL', 'value': self.pipeline.interval if self.pipeline.interval is not None else 'null'},
                {'key': 'HEADER_ATTRIBUTES', 'value': self.pipeline.header_attributes},
                {'key': 'metrics', 'value': {}},
            ],
            'script': script,
        }

    def _get_required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimensions_paths, self.pipeline.timestamp_path]]

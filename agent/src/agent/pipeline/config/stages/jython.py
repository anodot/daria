from . import base


class ConvertToMetrics30(base.Stage):
    JYTHON_SCRIPT = 'convert_to_metrics_30.py'

    def get_config(self) -> dict:
        return {
            'stageRequiredFields': self._get_required_fields(),
            'userParams': [
                {'key': 'TIMESTAMP_COLUMN', 'value': self.pipeline.timestamp_path},
                {'key': 'DIMENSIONS', 'value': self.pipeline.dimension_paths_with_names},
                {'key': 'MEASUREMENTS', 'value': self.pipeline.value_paths_with_names},
                {'key': 'COUNT_RECORDS', 'value': int(self.pipeline.count_records)},
                {'key': 'COUNT_RECORDS_MEASUREMENT_NAME', 'value': self.pipeline.count_records_measurement_name},
                {'key': 'HEADER_ATTRIBUTES', 'value': self.pipeline.header_attributes},
            ],
            'script': self._get_script(),
        }

    def _get_required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimension_paths, self.pipeline.timestamp_path]]

    def _get_script(self) -> str:
        with open(self.get_jython_file_path()) as f:
            script = f.read()
        return script.replace("'%TRANSFORM_SCRIPT_PLACEHOLDER%'", self.pipeline.transform_script_config or '')

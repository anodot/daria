import urllib.parse

from abc import ABC
from . import base


class Base(base.Stage, ABC):
    def _get_script(self) -> str:
        with open(self.get_jython_file_path()) as f:
            return f.read()


class ConvertToMetrics30(Base):
    JYTHON_SCRIPT = 'convert_to_metrics_30.py'

    def get_config(self) -> dict:
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
            'script': self._get_script(),
        }

    def _get_required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimensions_paths, self.pipeline.timestamp_path]]

    def _get_script(self) -> str:
        return super()._get_script().replace("'%TRANSFORM_SCRIPT_PLACEHOLDER%'", self.pipeline.transform_script_config or '')


class CreateWatermark(Base):
    JYTHON_SCRIPT = 'create_watermark.py'

    def get_config(self) -> dict:
        return {
            'userParams': [
                {'key': 'SLEEP_TIME', 'value': str(self.pipeline.watermark_sleep_time)},
                {'key': 'BUCKET_SIZE_IN_SECONDS', 'value': str(self.pipeline.flush_bucket_size.total_seconds())},
                {'key': 'SCHEMA_ID', 'value': self.pipeline.get_schema_id()},
                {
                    'key': 'PIPELINE_OFFSET_URL',
                    'value': urllib.parse.urljoin(
                        self.pipeline.streamsets.agent_external_url,
                        f'/pipelines/{self.pipeline.name}/offset'
                    )
                },
            ],
            'script': self._get_script(),
        }

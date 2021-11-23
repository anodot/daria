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
        return super()._get_script().replace("'%TRANSFORM_SCRIPT_PLACEHOLDER%'", self.pipeline.transform_script_config or '')


class CreateWatermark(Base):
    JYTHON_SCRIPT = 'create_watermark.py'

    def get_config(self) -> dict:
        return {
            'userParams': [
                {'key': 'SLEEP_TIME', 'value': str(self.pipeline.watermark_sleep_time)},
                {'key': 'SCHEMA_ID', 'value': self.pipeline.get_schema_id()},
                {
                    'key': 'CALCULATE_DIRECTORY_WATERMARK_URL',
                    'value': urllib.parse.urljoin(
                        self.pipeline.streamsets.agent_external_url,
                        f'/pipelines/{self.pipeline.name}/watermark'
                    )
                },
                {
                    'key': 'FILE_PROCESSED_MONITORING_ENDPOINT',
                    'value': urllib.parse.urljoin(
                        self.pipeline.streamsets.agent_external_url,
                        f'/monitoring/directory_file_processed/{self.pipeline.name}'
                    )
                },
                {
                    'key': 'WATERMARK_DELTA_MONITORING_ENDPOINT',
                    'value': urllib.parse.urljoin(
                        self.pipeline.streamsets.agent_external_url,
                        f'/monitoring/watermark_delta/{self.pipeline.name}'
                    )
                },
            ],
            'script': self._get_script(),
        }

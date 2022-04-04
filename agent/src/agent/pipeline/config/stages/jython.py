import urllib.parse

from .base import JythonProcessor


class ConvertToMetrics30(JythonProcessor):
    JYTHON_SCRIPT = 'convert_to_metrics_30.py'

    def get_config(self) -> dict:
        conf = super().get_config()
        conf['stageRequiredFields'] = self._get_required_fields()
        return conf

    def _get_required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimension_paths, self.pipeline.timestamp_path]]

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'TIMESTAMP_COLUMN',
                'value': self.pipeline.timestamp_path
            },
            {
                'key': 'DIMENSIONS',
                'value': self.pipeline.dimension_paths_with_names
            },
            {
                'key': 'MEASUREMENTS',
                'value': self.pipeline.value_paths_with_names
            },
            {
                'key': 'COUNT_RECORDS',
                'value': int(self.pipeline.count_records)
            },
            {
                'key': 'COUNT_RECORDS_MEASUREMENT_NAME',
                'value': self.pipeline.count_records_measurement_name
            },
            {
                'key': 'HEADER_ATTRIBUTES',
                'value': self.pipeline.header_attributes
            },
        ]


class CreateWatermark(JythonProcessor):
    JYTHON_SCRIPT = 'create_watermark.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'SLEEP_TIME',
                'value': str(self.pipeline.watermark_sleep_time)
            },
            {
                'key': 'SCHEMA_ID',
                'value': self.pipeline.get_schema_id()
            },
            {
                'key': 'CALCULATE_DIRECTORY_WATERMARK_URL',
                'value': urllib.parse.urljoin(
                    self.pipeline.streamsets.agent_external_url, f'/pipelines/{self.pipeline.name}/watermark'
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
                    self.pipeline.streamsets.agent_external_url, f'/monitoring/watermark_delta/{self.pipeline.name}'
                )
            },
        ]


class CreateEvents(JythonProcessor):
    JYTHON_SCRIPT = 'create_events.py'

    REQUIRED_EVENT_FIELDS = [
        'title',
        'category',
        # it will be required if it's not hardcoded in the jython script
        # 'source',
        'startDate'
    ]

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'EVENT_MAPPING',
                'value': {
                    'title': self.pipeline.config.get('mapping', {}).get('title', 'title'),
                    'description': self.pipeline.config.get('mapping', {}).get('description', 'description'),
                    'category': self.pipeline.config.get('mapping', {}).get('category', 'category'),
                    'source': self.pipeline.config.get('mapping', {}).get('source', 'source'),
                    'startDate': self.pipeline.config.get('mapping', {}).get('startDate', 'startDate'),
                    'endDate': self.pipeline.config.get('mapping', {}).get('endDate', 'endDate'),
                }
            },
            {
                'key': 'properties',
                'value': self.pipeline.config.get('mapping', {}).get('properties', 'properties')
            }
        ]

    def _get_required_fields(self) -> list:
        return [f'/{field}' for field in self.REQUIRED_EVENT_FIELDS]


# todo probably on pipeline creation we should create a topology user
class TopologyDestination(JythonProcessor):
    JYTHON_SCRIPT = 'topology_destination.py'

    def _get_script_params(self) -> list[dict]:
        return []


class ReplaceIllegalChars(JythonProcessor):
    JYTHON_SCRIPT = 'replace_illegal_chars.py'

    def _get_script_params(self) -> list[dict]:
        return []


class PromQLCreateMetrics(JythonProcessor):
    JYTHON_SCRIPT = 'promql_create_metrics.py'

    def _get_script_params(self) -> list[dict]:
        return []

import urllib.parse

from agent.modules import proxy, constants
from .base import JythonProcessor


class ConvertToMetrics30(JythonProcessor):
    JYTHON_SCRIPT = 'convert_to_metrics_30.py'

    def get_config(self) -> dict:
        conf = super().get_config()
        conf['stageRequiredFields'] = self._get_required_fields()
        return conf

    def _get_required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimension_paths, self.pipeline.timestamp_path]]

    def _get_tags_config(self) -> dict:
        return {name: value['value_path'] for name, value in self.pipeline.tag_configurations.items()}

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
            {
                'key': 'DYNAMIC_TAGS',
                'value': self._get_tags_config()
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


class JDBCCreateEvents(CreateEvents):
    def _get_script_params(self) -> list[dict]:
        return [
            *super(JDBCCreateEvents, self)._get_script_params(),
            {
                'key': "REQUIRED_FIELDS",
                'value': [field for field in self.REQUIRED_EVENT_FIELDS]
            }
        ]

    def _get_required_fields(self) -> list:
        return []


class TopologyDestination(JythonProcessor):
    JYTHON_SCRIPT = 'topology/destination.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'REQUEST_RETRIES',
                'value': constants.PIPELINE_REQUEST_RETRIES
            },
            {
                'key': 'RETRY_SLEEP_TIME_SECONDS',
                'value': constants.PIPELINE_RETRY_SLEEP_TIME_SECONDS
            },
            {
                'key': 'ANODOT_URL',
                'value': self.pipeline.destination.url
            },
            {
                'key': 'ACCESS_TOKEN',
                'value': self.pipeline.destination.access_key
            },
            {
                'key': 'PROXIES',
                'value': proxy.get_config(self.pipeline.destination.proxy)
            },
            {
                'key': 'LOG_EVERYTHING',
                'value': 'true' if self.pipeline.log_everything else 'false'
            },
        ]


class ReplaceIllegalChars(JythonProcessor):
    JYTHON_SCRIPT = 'replace_illegal_chars.py'

    def _get_script_params(self) -> list[dict]:
        return []


class PromQLCreateMetrics(JythonProcessor):
    JYTHON_SCRIPT = 'promql_create_metrics.py'

    def _get_script_params(self) -> list[dict]:
        return []

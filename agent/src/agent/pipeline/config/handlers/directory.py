from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.anodot_api_client import AnodotApiClient

logger = get_logger(__name__)


class DirectoryConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'directory_http.json'

    def replace_chars(self, property_name):
        return property_name.replace('/', '_').replace('.', '_').replace(' ', '_')

    def get_schema_id(self):
        measurements = {}
        for name, target_type in self.pipeline.config['values'].items():
            measurements[self.replace_chars(self.get_measurement_name(name))] = {
                'aggregation': 'sum' if target_type == 'counter' else 'average',
                'countBy': 'none'
            }
        if self.pipeline.config.get('count_records_measurement_name'):
            measurements[self.replace_chars(self.pipeline.config.get('count_records_measurement_name'))] = {
                'aggregation': 'sum',
                'countBy': 'none'
            }

        dimensions = self.get_dimensions() + list(self.pipeline.constant_dimensions.keys())
        schema = {
            'version': '1',
            'name': self.pipeline.id,
            'dimensions': [self.replace_chars(d) for d in dimensions],
            'measurements': measurements,
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }
        api_client = AnodotApiClient(self.pipeline.destination.api_key, self.pipeline.destination.get_proxy_configs(),
                                     base_url=self.pipeline.destination.url)
        if self.pipeline.config.get('schema'):
            if {key: val for key, val in self.pipeline.config['schema'].items() if key not in ['id']} == schema:
                return self.pipeline.config['schema']['id']
            api_client.delete_schema(self.pipeline.config['schema']['id'])

        self.pipeline.config.update(api_client.create_schema(schema))
        return self.pipeline.config['schema']['id']

    def update_pipeline_config(self):
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [
                    {'key': 'SCHEMA_ID', 'value': self.get_schema_id()},
                    {'key': 'TOKEN', 'value': self.pipeline.destination.token},
                    {'key': 'PROTOCOL', 'value': self.pipeline.destination.PROTOCOL_30},
                    {'key': 'ANODOT_BASE_URL', 'value': self.pipeline.destination.url},
                ]

    def update_destination_config(self):
        for stage in self.config['stages']:
            if stage['instanceName'] in ['destination', 'destination_watermark']:
                for conf in stage['configuration']:
                    if conf['name'] in self.pipeline.destination.config and conf['name'] != self.pipeline.destination.CONFIG_RESOURCE_URL:
                        conf['value'] = self.pipeline.destination.config[conf['name']]

    def update_stages(self, stage):
        super().update_stages(stage)
        if stage['instanceName'] == 'process_finish_file_event':
            self.process_finish_file_event_stage(stage)

    def process_finish_file_event_stage(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue
            extract_timestamp = "str:regExCapture(record:value('/filepath'), '.*/(.+)_.*', 1)"
            convert_timestamp_expr = self.get_convert_timestamp_to_unix_expression(extract_timestamp)
            bucket_size = self.pipeline.flush_bucket_size.total_seconds()
            watermark = f'math:floor(({convert_timestamp_expr} + {bucket_size})/{bucket_size}) * {bucket_size}'
            conf['value'] = [
                {
                    'fieldToSet': '/watermark',
                    'expression': '${' + watermark + '}'
                },
                {
                    'fieldToSet': '/schemaId',
                    'expression': self.pipeline.config['schema']['id']
                },
            ]

    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/dimensions/' + key

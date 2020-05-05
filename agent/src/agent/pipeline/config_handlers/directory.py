import urllib.parse
from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger
from agent.anodot_api_client import AnodotApiClient
from agent.constants import ANODOT_API_URL

logger = get_logger(__name__)


class DirectoryConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'directory_http.json'

    def replace_chars(self, property_name):
        return property_name.replace('/', '_').replace('.', '_').replace(' ', '_')

    def get_schema_id(self):
        measurements = {}
        for name, target_type in self.pipeline.config['values'].items():
            measurements[self.replace_chars(self.get_property_mapping(name))] = {
                'aggregation': 'sum' if target_type == 'counter' else 'average',
                'countBy': 'none'
            }
        schema = {
            'version': '1',
            'name': self.pipeline.id,
            'dimensions': [self.replace_chars(d) for d in self.get_dimensions()],
            'measurements': measurements,
            'missingDimPolicy': {
                'action': 'fill',
                'fill': 'NULL'
            }
        }
        api_client = AnodotApiClient(self.pipeline.destination)
        if self.pipeline.config.get('schema'):
            if {key: val for key, val in self.pipeline.config['schema'].items() if key not in ['id']} == schema:
                return self.pipeline.config['schema']['id']
            api_client.delete_schema(self.pipeline.config['schema_id'])

        self.pipeline.config.update(api_client.create_schema(schema))
        return self.pipeline.config['schema']['id']

    def update_pipeline_config(self):
        for config in self.config['configuration']:
            if config['name'] == 'constants':
                config['value'] = [{'key': 'schema_id', 'value': self.get_schema_id()}]

    def update_destination_config(self):
        self.pipeline.destination.config[self.pipeline.destination.CONFIG_RESOURCE_URL] = urllib.parse.urljoin(
            ANODOT_API_URL, f'api/v1/metrics?token={self.config["token"]}&protocol=protocol30')

        super().update_destination_config()

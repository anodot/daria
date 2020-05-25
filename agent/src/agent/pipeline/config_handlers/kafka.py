from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger
from ...source import KafkaSource

logger = get_logger(__name__)


class KafkaConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'kafka_http.json'
    target_types = ['counter', 'gauge', 'running_counter']

    def override_stages(self):
        # using 'anodot_agent_' + self.id as a default value in order not to break old configs
        if KafkaSource.CONFIG_CONSUMER_GROUP not in self.pipeline.override_source:
            self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] = 'anodot_agent_' + self.pipeline.id
        self.update_source_configs()

        # for old config <=v1.4
        if 'value' in self.client_config and 'values' not in self.client_config:
            if self.client_config['value']['type'] == 'constant':
                self.client_config['count_records'] = True
                self.client_config['count_records_measurement_name'] = self.client_config['measurement_name']
                self.client_config['values'] = {}
                self.client_config['measurement_names'] = {}
            else:
                self.client_config['values'] = {self.client_config['value']['value']: self.client_config['target_type']}
                self.client_config['measurement_names'] = {
                    self.client_config['value']['value']: self.client_config['measurement_name']}

        for stage in self.config['stages']:
            self.update_stages(stage)

        self.update_destination_config()

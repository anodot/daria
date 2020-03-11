from .schemaless import SchemalessConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class KafkaConfigHandler(SchemalessConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'kafka_http.json'

    def override_stages(self):
        self.client_config['source']['config']['conf.consumerGroup'] = 'anodot_agent_' + self.get_pipeline_id()
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

        self.update_stages()

        self.update_destination_config()

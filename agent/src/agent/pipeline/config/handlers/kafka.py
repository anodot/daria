from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.source import KafkaSource
from agent.pipeline.config.stages import JSConvertMetrics20, AddProperties, Filtering, Destination, Source, Pivoter

logger = get_logger(__name__)


class KafkaConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'kafka_http.json'

    stages = {
        'source': Source,
        'FieldPivoter_01': Pivoter,
        'JavaScriptEvaluator_01': JSConvertMetrics20,
        'ExpressionEvaluator_02': AddProperties,
        'ExpressionEvaluator_03': Filtering,
        'destination': Destination
    }

    def override_stages(self):
        # using 'anodot_agent_' + self.id as a default value in order not to break old configs
        if KafkaSource.CONFIG_CONSUMER_GROUP not in self.pipeline.override_source:
            self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] = 'anodot_agent_' + self.pipeline.id

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

        super().override_stages()

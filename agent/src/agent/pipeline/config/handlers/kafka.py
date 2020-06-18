from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.source import KafkaSource
from agent.pipeline.config.stages import JSConvertMetrics, AddProperties, Filtering, Destination, Source

logger = get_logger(__name__)


class KafkaConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'kafka_http.json'

    stages = {
        'source': Source,
        'JavaScriptEvaluator_01': JSConvertMetrics,
        'ExpressionEvaluator_02': AddProperties,
        'ExpressionEvaluator_03': Filtering,
        'destination': Destination
    }

    def override_stages(self):
        # using 'anodot_agent_' + self.id as a default value in order not to break old configs
        if KafkaSource.CONFIG_CONSUMER_GROUP not in self.pipeline.override_source:
            if KafkaSource.CONFIG_CONSUMER_GROUP in self.pipeline.config:
                self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] = \
                    self.pipeline.config[KafkaSource.CONFIG_CONSUMER_GROUP]
            else:
                self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] = 'anodot_agent_' + self.pipeline.id

        super().override_stages()

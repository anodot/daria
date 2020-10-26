from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.source import KafkaSource
from agent.pipeline.config import stages

logger = get_logger(__name__)


class KafkaConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'kafka_http.json'

    stages_to_override = {
        'source': stages.schemaless_source.SchemalessSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }

    def override_stages(self):
        # using 'anodot_agent_' + self.id as a default value in order not to break old configs
        if KafkaSource.CONFIG_CONSUMER_GROUP not in self.pipeline.override_source:
            self.pipeline.override_source[KafkaSource.CONFIG_CONSUMER_GROUP] = 'anodot_agent_' + self.pipeline.name

        super().override_stages()

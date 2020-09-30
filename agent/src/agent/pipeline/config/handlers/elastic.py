from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.source import ElasticSource

logger = get_logger(__name__)


class ElasticConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'elastic_http.json'

    stages_to_override = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }

    def override_stages(self):
        self.pipeline.source.config[ElasticSource.CONFIG_QUERY] = self.pipeline.query
        super().override_stages()

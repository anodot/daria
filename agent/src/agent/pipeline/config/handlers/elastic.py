from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config import stages
from agent.source import ElasticSource

logger = get_logger(__name__)


class ElasticConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'elastic_http.json'

    stages = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }

    def override_stages(self):
        with open(self.pipeline.config['query_file']) as f:
            self.pipeline.source.config[ElasticSource.CONFIG_QUERY] = f.read()
        super().override_stages()

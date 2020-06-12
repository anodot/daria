from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config.stages import JSConvertMetrics20, AddProperties, Filtering, Destination, Source
from agent.source import ElasticSource

logger = get_logger(__name__)


class ElasticConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'elastic_http.json'

    stages = {
        'source': Source,
        'JavaScriptEvaluator_01': JSConvertMetrics20,
        'ExpressionEvaluator_02': AddProperties,
        'ExpressionEvaluator_03': Filtering,
        'destination': Destination
    }

    def override_stages(self):
        with open(self.pipeline.config['query_file']) as f:
            self.pipeline.source.config[ElasticSource.CONFIG_QUERY] = f.read()
        super().override_stages()

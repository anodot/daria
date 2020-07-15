from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline import pipeline

logger = get_logger(__name__)


class VictoriaConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'victoria_http.json'

    # stages = {
    #     'source': stages.sage_source.SageScript,
    #     'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
    #     'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
    #     'destination': stages.destination.Destination
    # }
    #
    # def override_stages(self):
    #     self.pipeline.config['timestamp'] = {
    #         'name': '@timestamp',
    #         'type': pipeline.TimestampType.UTC_STRING.value
    #     }
    #     super().override_stages()

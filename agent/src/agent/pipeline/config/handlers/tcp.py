from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, TestConfigHandler

logger = get_logger(__name__)


class TCPConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }


class TestTCPConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
    }

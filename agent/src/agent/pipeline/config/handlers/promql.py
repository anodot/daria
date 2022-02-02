from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class PromQLConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.promql.PromQLScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }


class PromQLSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.promql.PromQLSchemaScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'JythonEvaluator_01': stages.jython.ReplaceIllegalChars,
        'destination': stages.destination.Destination
    }


class TestPromQLConfigHandler(PromQLConfigHandler):
    stages_to_override = {
        'source': stages.source.promql.TestPromQLScript,
    }

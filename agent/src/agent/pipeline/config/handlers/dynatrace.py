from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import SchemaConfigHandler

logger = get_logger(__name__)


class DynatraceSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.dynatrace.DynatraceScript,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.SageJSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination
    }

from .base import BaseConfigHandler
from .schema import SchemaConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages


logger = get_logger(__name__)


class KafkaConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }


class KafkaSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'js_pivot_array': stages.js_pivot_array.JSPivotArray,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }

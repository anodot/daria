from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import BaseConfigHandler
from agent.pipeline.config.handlers.schema import SchemaConfigHandler

logger = get_logger(__name__)


class JDBCSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc_offset.JDBCScript,
        'source': stages.source.jdbc.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'destination': stages.destination.Destination
    }


class JDBCConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc_offset.JDBCScript,
        'source': stages.source.jdbc.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

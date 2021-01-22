from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.streamsets.config_handlers.base import BaseConfigHandler
from agent.streamsets.config_handlers.schema import SchemaConfigHandler

logger = get_logger(__name__)


class JDBCConfigHandlerProtocol3(SchemaConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc_offset.JDBCScript,
        'source': stages.jdbc_source.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'destination': stages.destination.Destination
    }


class JDBCConfigHandlerProtocol2(BaseConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc_offset.JDBCScript,
        'source': stages.jdbc_source.JDBCSource,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

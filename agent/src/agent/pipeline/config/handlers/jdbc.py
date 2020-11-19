from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class JDBCConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'offset': stages.jdbc_source.JDBCScript,
        'source': stages.jdbc_lookup.JDBCLookupStage,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

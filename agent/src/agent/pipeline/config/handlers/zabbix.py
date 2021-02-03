from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class ZabbixConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.zabbix_source.ZabbixScript,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

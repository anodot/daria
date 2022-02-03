from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import TestConfigHandler, NoSchemaConfigHandler

logger = get_logger(__name__)


class ZabbixConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.zabbix.ZabbixScript,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }


class TestZabbixConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.zabbix.TestZabbixScript,
    }

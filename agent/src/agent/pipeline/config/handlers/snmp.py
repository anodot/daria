from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import SchemaConfigHandler, BaseRawConfigHandler

logger = get_logger(__name__)


class SNMPConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.snmp.SNMP,
        'ExpressionEvaluator_02': stages.expression_evaluator.Filtering,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination,
    }


class SNMPRawConfigHandler(BaseRawConfigHandler):
    stages_to_override = {
        'source': stages.source.snmp.SNMPRaw,
        'HTTPClient_01': stages.destination.HttpDestination,
    }

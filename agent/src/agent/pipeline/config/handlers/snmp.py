from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class SNMPConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.snmp.SNMP,
        'ExpressionEvaluator_02': stages.expression_evaluator.Filtering,
        'FieldRenamer_01': stages.field_renamer.SchemaDimensionsRenamer,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination,
    }


class SNMPRawConfigHandler(BaseConfigHandler):
    # todo надо еще отправлять откуда и как мы эти данные достали
    stages_to_override = {
        'source': stages.source.snmp.SNMPRaw,
    }

from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class ObserviumConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
        'FieldRenamer_01': stages.field_renamer.SchemaDimensionsRenamer,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.schema import SchemaConfigHandler

logger = get_logger(__name__)


class ObserviumConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
        'FieldRenamer_01': stages.field_renamer.SchemaDimensionsRenamer,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

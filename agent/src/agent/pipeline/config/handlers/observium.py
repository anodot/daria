from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class ObserviumConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }


class TestObserviumConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.TestObserviumScript,
    }

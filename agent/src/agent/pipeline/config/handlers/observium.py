from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import SchemaConfigHandler, TestConfigHandler

logger = get_logger(__name__)


class ObserviumConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'replace_illegal_chars': stages.jython.ReplaceIllegalChars,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }


class TestObserviumConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.observium.ObserviumScript,
    }

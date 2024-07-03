from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import SchemaConfigHandler, TestConfigHandler

logger = get_logger(__name__)


class ActianConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.actian.ActianScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'replace_illegal_chars': stages.jython.ReplaceIllegalChars,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination
    }

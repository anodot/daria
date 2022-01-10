from agent import pipeline
from agent.modules.logger import get_logger
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler

logger = get_logger(__name__)


class PromQLConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.promql.PromQLScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

    def _override_stages(self):
        self.pipeline.config['timestamp'] = {
            'type': pipeline.TimestampType.UNIX.value
        }
        super()._override_stages()


class TestPromQLConfigHandler(PromQLConfigHandler):
    stages_to_override = {
        'source': stages.source.promql.TestPromQLScript,
    }

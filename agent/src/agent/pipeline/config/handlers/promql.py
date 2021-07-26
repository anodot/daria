from agent import pipeline
from .base import BaseConfigHandler
from agent.modules.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class PromQLConfigHandler(BaseConfigHandler):
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

from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import BaseConfigHandler


class CactiConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.cacti.Cacti,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination,
    }

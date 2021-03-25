from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import BaseConfigHandler


class CactiConfigHandler(BaseConfigHandler):
    stages_to_override = {
        'source': stages.source.cacti.Cacti,
        'ExpressionEvaluator_02': stages.expression_evaluator.Filtering,
        'FieldRenamer_01': stages.field_renamer.CactiDimensionsRenamer,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination,
    }

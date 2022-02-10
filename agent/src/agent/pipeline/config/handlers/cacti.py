from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler


class CactiConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.cacti.Cacti,
        'ExpressionEvaluator_02': stages.expression_evaluator.Filtering,
        'FieldRenamer_01': stages.field_renamer.DimensionsRenamer,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'JythonEvaluator_01': stages.jython.ReplaceIllegalChars,
        'destination': stages.destination.Destination,
    }

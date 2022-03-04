from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler


class RRDConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.rrd.RRD,
        'ExpressionEvaluator_01': stages.expression_evaluator.AddProperties,
        'JythonEvaluator_01': stages.jython.ReplaceIllegalChars,
        'destination': stages.destination.Destination,
    }

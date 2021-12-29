from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler


class TopologyConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.topology.TopologyScript,
        'JythonEvaluator_01': stages.jython.TopologyDestination,
    }

from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import NoSchemaConfigHandler


class HttpConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.http.Http,
        'JythonEvaluator_02': stages.topology.TopologyScript,
        'JythonEvaluator_01': stages.jython.TopologyDestination,
    }


class DirectoryConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JythonEvaluator_03': stages.topology.DirectoryCsvToJson,
        'JythonEvaluator_02': stages.topology.TopologyScript,
        'JythonEvaluator_01': stages.jython.TopologyDestination,
    }

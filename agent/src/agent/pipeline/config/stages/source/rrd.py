from agent.pipeline.config.stages.source.cacti import Cacti


class RRD(Cacti):
    JYTHON_SCRIPT = 'cacti.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractor/rrd'

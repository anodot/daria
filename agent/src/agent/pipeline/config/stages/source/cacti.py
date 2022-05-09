from agent.pipeline.config.stages.source.rrd import RRD


class Cacti(RRD):
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractor/cacti'

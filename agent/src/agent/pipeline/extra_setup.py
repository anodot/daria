import json

from agent import source
from agent.data_extractor import cacti
from agent.pipeline import Pipeline
from agent.modules import logger

logger_ = logger.get_logger(__name__, stdout=True)


def do(pipeline_: Pipeline):
    if pipeline_.source.type == source.TYPE_CACTI:
        logger_.info('Caching Cacti data, please wait..')
        cacti.cacher.cache_pipeline_data(pipeline_, force=True)
        logger_.info('Caching data complete')
    elif pipeline_.source.type == source.TYPE_ZABBIX:
        if pipeline_.config.get('query_changed', False) and pipeline_.offset:
            # remove last item id from offset because query changed
            json_offset = json.loads(pipeline_.offset.offset)
            offset_value = json_offset["offsets"][""]
            offset_value = offset_value.split("_")[0]
            json_offset["offsets"][""] = offset_value
            pipeline_.offset.offset = json.dumps(json_offset)
            del pipeline_.config['query_changed']

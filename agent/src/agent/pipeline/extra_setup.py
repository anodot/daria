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

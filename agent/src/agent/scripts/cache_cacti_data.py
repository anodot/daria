import time

from agent import monitoring
from agent.data_extractor import cacti
from agent.modules import logger

logger_ = logger.get_logger(__name__)

SCRIPT_NAME = 'cache_cacti_data'

start = time.time()
if __name__ == '__main__':
    try:
        cacti.cacher.cache_data()
        monitoring.set_scheduled_script_execution_time(SCRIPT_NAME, time.time() - start)
    except Exception as e:
        logger_.error(str(e))
        monitoring.increase_scheduled_script_error_counter(SCRIPT_NAME)
        raise

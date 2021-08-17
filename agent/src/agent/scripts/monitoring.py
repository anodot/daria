import time

from agent import monitoring
from agent.modules import logger

logger_ = logger.get_logger(__name__)

SCRIPT_NAME = 'monitoring'

start = time.time()
if __name__ == '__main__':
    try:
        monitoring.run()
        monitoring.set_scheduled_script_execution_time(SCRIPT_NAME, time.time() - start)
    except Exception as e:
        logger_.error(str(e))
        monitoring.increase_scheduled_script_error_counter(SCRIPT_NAME)
        raise
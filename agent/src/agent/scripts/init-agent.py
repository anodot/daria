import os
import time
import traceback
import sdc_client

from agent import pipeline, di
from agent.modules import logger

di.init()
logger = logger.get_logger(__name__)

IGNORE_INIT_SCRIPT_FAILURES = os.environ.get('IGNORE_INIT_SCRIPT_FAILURES', 'false').lower() == 'true'
NUMBER_OF_RETRIES = 4
RETRY_SLEEP = 20


def main():
    i = NUMBER_OF_RETRIES
    while True:
        try:
            _update_pipeline_statuses()
        except Exception as e:
            if i > 0:
                logger.info(f'Init script failed, retrying in {RETRY_SLEEP} seconds...')
                i -= 1
                time.sleep(RETRY_SLEEP)
                continue

            logger.error(traceback.format_exc())
            if not IGNORE_INIT_SCRIPT_FAILURES:
                raise InitScriptException(
                    'Agent init script failed. You can set the '
                    '`IGNORE_INIT_SCRIPT_FAILURES` environment variable to `true` to start the container anyway'
                ) from e
        break


def _update_pipeline_statuses():
    statuses = sdc_client.get_all_pipeline_statuses()
    for pipeline_ in pipeline.repository.get_all():
        if pipeline_.name in statuses:
            pipeline_.status = statuses[pipeline_.name]['status']
            pipeline.repository.save(pipeline_)


class InitScriptException(Exception):
    pass


if __name__ == '__main__':
    logger.info('Agent init script started')
    main()
    logger.info('Agent init script finished successfully')

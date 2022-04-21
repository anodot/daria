import os
import traceback
import sdc_client

from agent import pipeline, di
from agent.modules import logger

di.init()
logger = logger.get_logger(__name__)

IGNORE_INIT_SCRIPT_FAILURES = os.environ.get('IGNORE_INIT_SCRIPT_FAILURES', 'false').lower() == 'true'


def main():
    try:
        statuses = sdc_client.get_all_pipeline_statuses()
        for pipeline_ in pipeline.repository.get_all():
            if pipeline_.name in statuses:
                pipeline_.status = statuses[pipeline_.name]['status']
                pipeline.repository.save(pipeline_)
    except Exception as e:
        logger.error(traceback.format_exc())

        if not IGNORE_INIT_SCRIPT_FAILURES:
            raise InitScriptException(
                'Agent init script failed. You can set the '
                '`IGNORE_INIT_SCRIPT_FAILURES` environment variable to `true` to start the container anyway'
            ) from e


class InitScriptException(Exception):
    pass


if __name__ == '__main__':
    main()

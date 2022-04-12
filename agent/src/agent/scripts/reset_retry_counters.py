import traceback
from datetime import datetime
from agent import pipeline, monitoring
from agent.modules.logger import get_logger
from agent.modules import constants

logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors: int):
    monitoring.increase_scheduled_script_error_counter('reset_retry_counters')
    return num_of_errors + 1


def main():
    num_of_errors = 0
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    for pipeline_ in pipelines:
        try:
            last_updated_in_min = int((datetime.now() - pipeline_.retries.last_updated).total_seconds() / 60)
            if last_updated_in_min - constants.STREAMSETS_NOTIFY_RESET_AFTER_MIN > 0:
                pipeline.manager.reset_pipeline_retries(pipeline_)
                pipeline.manager.set_pipeline_retries_notification_sent(pipeline_, False)
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(f'Error resetting pipeline {pipeline_.name} retry counter')
            logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())

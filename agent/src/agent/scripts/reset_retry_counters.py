import traceback
from datetime import datetime
from agent import pipeline, monitoring
from agent.modules.logger import get_logger
from agent.modules import constants
from agent.pipeline import Pipeline, notifications

logger = get_logger(__name__, stdout=True)

num_of_errors = 0


def _update_errors_count():
    monitoring.increase_scheduled_script_error_counter('reset_retry_counters')
    global num_of_errors
    num_of_errors += 1


def log_error(message):
    _update_errors_count()
    logger.error(traceback.format_exc())


def _reset_retries(pipeline_: Pipeline):
    if not pipeline_.retries:
        return
    try:
        if not pipeline_.retries.last_updated:
            pipeline.manager.reset_pipeline_retries(pipeline_)
        else:
            last_updated_in_min = int((datetime.now() - pipeline_.retries.last_updated).total_seconds() / 60)
            if last_updated_in_min - constants.STREAMSETS_NOTIFY_RESET_AFTER_MIN > 0:
                pipeline.manager.reset_pipeline_retries(pipeline_)
    except Exception:
        log_error(f'Error resetting pipeline {pipeline_.name} retry counter')


def _reset_notifications(pipeline_: Pipeline):
    if not (pipeline_.notifications
            and pipeline_.notifications.no_data_notification
            and pipeline_.notifications.no_data_notification.notification_sent):
        return
    try:
        if not pipeline_.notifications.no_data_notification.last_updated:
            pipeline.manager.reset_pipeline_notifications(pipeline_)
        else:
            last_updated_in_min = int((datetime.now() - pipeline_.notifications.no_data_notification.last_updated).total_seconds() / 60)
            if last_updated_in_min - constants.STREAMSETS_NOTIFY_RESET_AFTER_MIN > 0:
                pipeline.manager.reset_pipeline_notifications(pipeline_)
    except Exception:
        log_error(f'Error resetting pipeline {pipeline_.name} notifications')


def main():
    num_of_errors = 0
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count()
        raise

    for pipeline_ in pipelines:
        _reset_retries(pipeline_)
        _reset_notifications(pipeline_)

    return num_of_errors


if __name__ == '__main__':
    main()
    exit(num_of_errors)

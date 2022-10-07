import traceback

from agent import pipeline, monitoring, di
from agent.modules.logger import get_logger
from agent.modules import constants

if not constants.SEND_WATERMARKS_BY_CRON:
    exit(0)

logger = get_logger(__name__, stdout=True)
di.init()


def main():
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    num_of_errors = 0
    for pipeline_ in pipelines:
        try:
            watermark_manager = pipeline.watermark.PeriodicWatermarkManager(pipeline_)
            if not watermark_manager.should_send_watermark():
                continue

            with pipeline.repository.SessionManager(pipeline_):
                next_bucket_start = watermark_manager.get_latest_bucket_start()
                pipeline.watermark.send_to_anodot(pipeline_, next_bucket_start)
                pipeline.manager.update_pipeline_watermark(pipeline_, next_bucket_start)
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(f'Error sending pipeline watermark {pipeline_.name}')
            logger.error(traceback.format_exc())
    return num_of_errors


def _update_errors_count(num_of_errors):
    monitoring.increase_scheduled_script_error_counter('periodic-watermark')
    return num_of_errors + 1


if __name__ == '__main__':
    exit(main())

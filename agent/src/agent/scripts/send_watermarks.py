import time
import traceback
import anodot

from datetime import datetime
from agent import pipeline, destination, monitoring, di
from agent.destination.anodot_api_client import AnodotApiClient
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
        watermark_manager = pipeline.watermark.PeriodicWatermarkManager(pipeline_)
        if watermark_manager.should_send_watermark():
            try:
                with pipeline.repository.SessionManager(pipeline_):
                    next_bucket_start = watermark_manager.get_latest_bucket_start()
                    pipeline.manager.update_pipeline_watermark(pipeline_, next_bucket_start)

                    watermark = anodot.Watermark(pipeline_.get_schema_id(), datetime.fromtimestamp(next_bucket_start))
                    AnodotApiClient(destination.repository.get()).send_watermark(watermark.to_dict())

                    logger.debug(f'Sent watermark for `{pipeline_.name}`, value: {pipeline_.watermark.timestamp}')
                    monitoring.set_watermark_delta(pipeline_.name, time.time() - pipeline_.watermark.timestamp)
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

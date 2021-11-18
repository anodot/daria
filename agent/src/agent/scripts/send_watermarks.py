import time
import traceback
import anodot

from agent import pipeline, destination, monitoring
from agent.modules.logger import get_logger
from agent.modules import constants
from anodot import api_client

if not constants.SEND_WATERMARKS_BY_CRON:
    exit(0)

logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors):
    monitoring.increase_scheduled_script_error_counter('periodic-watermark')
    return num_of_errors + 1


def main():
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    num_of_errors = 0
    for pipeline_ in pipelines:
        if pipeline_.uses_schema \
                and pipeline_.periodic_watermark_config and pipeline_.offset \
                and pipeline_.offset.timestamp + pipeline_.watermark_delay <= time.time():
            try:
                watermark = pipeline.manager.get_next_bucket_start(
                    pipeline_.periodic_watermark_config['bucket_size'],
                    pipeline_.offset.timestamp
                )
                destination_ = destination.repository.get()
                api_client.send_watermark(
                    anodot.Watermark(pipeline_.get_schema_id(), watermark),
                    destination_.token,
                    logger,
                    destination_.url
                )
                logger.info(f'Sent watermark for `{pipeline_.name}`, value: {watermark.timestamp()}')
            except Exception:
                num_of_errors = _update_errors_count(num_of_errors)
                logger.error(f'Error sending pipeline watermark {pipeline_.name}')
                logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())

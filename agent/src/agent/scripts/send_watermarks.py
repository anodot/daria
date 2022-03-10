import time
import traceback
import anodot

from agent import pipeline, destination, monitoring
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger
from agent.modules import constants

if not constants.SEND_WATERMARKS_BY_CRON:
    exit(0)

logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors):
    monitoring.increase_scheduled_script_error_counter('periodic-watermark')
    return num_of_errors + 1


def _should_send_watermark(pipeline_: pipeline.Pipeline):
    return pipeline_.uses_schema \
           and pipeline_.periodic_watermark_config and pipeline_.offset \
           and pipeline_.offset.timestamp + pipeline_.watermark_delay <= time.time()


def main():
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    num_of_errors = 0
    for pipeline_ in pipelines:
        if not _should_send_watermark(pipeline_):
            continue
        try:
            next_bucket_start = pipeline.manager.get_next_bucket_start(
                pipeline_.periodic_watermark_config['bucket_size'],
                pipeline_.offset.timestamp
            )
            watermark = anodot.Watermark(pipeline_.get_schema_id(), next_bucket_start).to_dict()
            AnodotApiClient(destination.repository.get()).send_watermark(watermark)
            logger.debug(f'Sent watermark for `{pipeline_.name}`, value: {next_bucket_start.timestamp()}')
            monitoring.set_watermark_delta(pipeline_.name, time.time() - next_bucket_start.timestamp())
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(f'Error sending pipeline watermark {pipeline_.name}')
            logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())

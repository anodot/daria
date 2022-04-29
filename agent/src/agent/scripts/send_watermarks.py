import time
import traceback
import anodot

from datetime import datetime
from agent import pipeline, destination, monitoring, source
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger
from agent.modules import constants
from agent.pipeline import Pipeline, FlushBucketSize

if not constants.SEND_WATERMARKS_BY_CRON:
    exit(0)

logger = get_logger(__name__, stdout=True)


def main():
    try:
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    num_of_errors = 0
    for pipeline_ in pipelines:
        if _should_send_watermark(pipeline_):
            try:
                with pipeline.repository.SessionManager(pipeline_):
                    next_bucket_start = _get_latest_bucket_start(pipeline_)
                    pipeline_.watermark.timestamp = next_bucket_start.timestamp()

                    watermark = anodot.Watermark(pipeline_.get_schema_id(), next_bucket_start).to_dict()
                    AnodotApiClient(destination.repository.get()).send_watermark(watermark)

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


def _should_send_watermark(pipeline_: Pipeline):
    if pipeline_.source_.type == source.TYPE_DIRECTORY:
        return _should_send_force_watermark(pipeline_)
    return _should_send_periodic_watermark(pipeline_)


def _should_send_force_watermark(pipeline_: Pipeline):
    return pipeline_.uses_schema and pipeline_.dvp_config \
           and pipeline_.periodic_watermark_config and pipeline_.watermark \
           and not _is_latest_watermark(pipeline_.watermark.timestamp, pipeline_.watermark_delay)


def _should_send_periodic_watermark(pipeline_: Pipeline):
    #  todo maybe I should check watermark here as well instead of offset?
    return pipeline_.uses_schema \
           and pipeline_.periodic_watermark_config and pipeline_.offset \
           and time.time() - pipeline_.offset.timestamp >= pipeline_.watermark_delay


def _get_latest_bucket_start(pipeline_: Pipeline) -> datetime:
    if pipeline_.source_.type == source.TYPE_DIRECTORY:
        return _get_latest_directory_bucket_start(
            pipeline_.flush_bucket_size, pipeline_.watermark.timestamp, pipeline_.watermark_delay
        )
    return _get_latest_periodic_bucket_start(
        pipeline_.periodic_watermark_config['bucket_size'], pipeline_.offset, pipeline_.watermark_delay
    )


def _get_latest_directory_bucket_start(bucket_size: FlushBucketSize, watermark: int, delay: int) -> datetime:
    while not _is_latest_watermark(watermark, delay):
        watermark += bucket_size.total_seconds()
    return datetime.fromtimestamp(watermark)


def _get_latest_periodic_bucket_start(bucket_size: str, watermark: int, delay: int) -> datetime:
    # todo should I return latest here or it might be not latest?
    while not _is_latest_watermark(watermark, delay):
        watermark = pipeline.manager.get_next_bucket_start(bucket_size, watermark)
    return watermark


def _is_latest_watermark(watermark: int, delay: int):
    return time.time() - watermark <= delay


if __name__ == '__main__':
    exit(main())

import time
import traceback
import requests

from datetime import datetime, timedelta, timezone
from agent import pipeline, destination, monitoring
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger
from agent.modules import constants
from agent.pipeline import Pipeline

if not constants.SEND_WATERMARKS_BY_CRON:
    exit(0)

logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors):
    monitoring.increase_scheduled_script_error_counter('agent-to-bc')
    return num_of_errors + 1


def _get_next_bucket_start(pipeline_: Pipeline) -> float:
    bs = pipeline_.periodic_watermark_config['bucket_size']
    dt = datetime.fromtimestamp(pipeline_.offset.timestamp).replace(tzinfo=timezone.utc)
    if bs == pipeline.FlushBucketSize.MIN_1:
        return (dt.replace(second=0, microsecond=0) + timedelta(minutes=1)).timestamp()
    elif bs == pipeline.FlushBucketSize.MIN_5:
        return (dt.replace(second=0, microsecond=0) + timedelta(minutes=5 - dt.minute % 5)).timestamp()
    elif bs == pipeline.FlushBucketSize.HOUR_1:
        return (dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).timestamp()
    elif bs == pipeline.FlushBucketSize.DAY_1:
        return (dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).timestamp()
    raise Exception('Invalid bucket size provided')


def main():
    try:
        api_client = AnodotApiClient(destination.repository.get(), AnodotApiClient.V1)
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    num_of_errors = 0
    for pipeline_ in pipelines:
        if pipeline_.uses_schema \
                and pipeline_.periodic_watermark_config \
                and pipeline_.offset.timestamp + pipeline_.watermark_delay <= time.time():
            try:
                api_client.send_watermark_to_bc(pipeline_.get_schema_id(), _get_next_bucket_start(pipeline_))
            except requests.HTTPError as e:
                if not e.response.status_code == 404:
                    num_of_errors = _update_errors_count(num_of_errors)
                    logger.error(traceback.format_exc())
            except Exception:
                num_of_errors = _update_errors_count(num_of_errors)
                logger.error(f'Error sending pipeline watermark {pipeline_.name}')
                logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())

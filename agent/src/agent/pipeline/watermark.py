import pytz

from datetime import datetime, timezone, timedelta
from agent import pipeline
from agent.pipeline import Pipeline


class PeriodicWatermarkManager:
    """
    This class is responsible for the logic of sending watermarks to Anodot periodically for pipelines that can't
    send watermarks directly from StreamSets.
    It is possible to send watermarks only for pipelines that use protocol30 (protocol20 doesn't have watermarks)
    and have a periodic_watermark configuration.
    Also, the pipeline must be running, if it's not running and the watermark is sent, when the pipeline is started
    the data with a timestamp less than watermark might be sent and thus will be lost.


    The watermark should be sent in two cases:
    1. The pipeline doesn't have a watermark, but it has an offset, i.e. it already sent some data to Anodot.
    And the next watermark value, which is calculated based on this offset, is less than `now - watermark_delay`
    2. The pipeline has a watermark that was sent previously, and the next watermark value
    is less than `now - watermark_delay`

    This logic is deliberately ignoring some edge cases, like when the pipeline is sending historical data, because
    taking into account everything makes the logic too complex.
    """

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.timezone_ = pytz.timezone(pipeline_.timezone)

    def should_send_watermark(self) -> bool:
        # the commented method might be useful in situations when we have problems with loading historical data
        # and not self._is_recent_offset(pipeline_) \
        return pipeline.manager.is_running(self.pipeline) and self.pipeline.uses_schema() \
               and self.pipeline.has_offset() \
               and self.pipeline.has_periodic_watermark_config() \
               and (
                       (self.pipeline.has_watermark() and self._watermark_delay_passed())
                       or (not self.pipeline.has_watermark() and self._offset_delay_passed())
               )

    # @staticmethod
    # def _is_recent_offset(pipeline_: Pipeline) -> bool:
    #     return self.pipeline.offset.updated_at > self._get_local_now_timestamp() \
    #            - pipeline.FlushBucketSize(self.pipeline.periodic_watermark_config['bucket_size']).total_seconds()

    def _watermark_delay_passed(self) -> bool:
        return self._get_now_timestamp() >= self.pipeline.watermark.timestamp \
               + pipeline.FlushBucketSize(self.pipeline.periodic_watermark_config['bucket_size']).total_seconds() \
               + self.pipeline.watermark_delay

    def _offset_delay_passed(self) -> bool:
        next_bucket_start = get_next_bucket_start(
            self.pipeline.periodic_watermark_config['bucket_size'], self.pipeline.offset.timestamp
        )
        return self._get_now_timestamp() >= next_bucket_start.timestamp() + self.pipeline.watermark_delay

    def get_latest_bucket_start(self) -> int:
        delay = self.pipeline.watermark_delay
        bs_secs = pipeline.FlushBucketSize(self.pipeline.periodic_watermark_config['bucket_size']).total_seconds()

        watermark_timestamp = self._get_current_watermark()
        while not self._is_latest_watermark(watermark_timestamp, delay, bs_secs):
            watermark_timestamp += bs_secs
        return watermark_timestamp

    def _get_current_watermark(self) -> int:
        if self.pipeline.watermark:
            return self.pipeline.watermark.timestamp
        elif self.pipeline.offset:
            return int(get_next_bucket_start(
                self.pipeline.periodic_watermark_config['bucket_size'], self.pipeline.offset.timestamp
            ).timestamp())
        raise WatermarkCalculationException(
            f'No watermark or offset for the pipeline `{self.pipeline.name}`'
        )

    def _is_latest_watermark(self, watermark: int, delay: int, bucket_size: int):
        # everything is in seconds
        return self._get_now_timestamp() - delay - watermark < bucket_size

    def _get_now_timestamp(self) -> int:
        dt = datetime.utcnow()
        return int(dt.timestamp())


def get_next_bucket_start(bs: str, offset: float) -> datetime:
    dt = datetime.fromtimestamp(offset, tz=timezone.utc)
    if bs == pipeline.FlushBucketSize.MIN_1:
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
    elif bs == pipeline.FlushBucketSize.MIN_5:
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=5 - dt.minute % 5)
    elif bs == pipeline.FlushBucketSize.HOUR_1:
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    elif bs == pipeline.FlushBucketSize.DAY_1:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    raise WatermarkCalculationException('Invalid bucket size provided')


class WatermarkCalculationException(Exception):
    pass

import pytest
import pytz

from unittest.mock import Mock
from datetime import datetime, timedelta
from agent import pipeline


@pytest.mark.parametrize(
    "now, watermark, offset, watermark_delay, bucket_size, uses_schema, er", [
        (100, None, None, 10, '5m', True, False),
        (100, None, None, 10, '5m', False, False),
        (1200, 1200 - 450, 1000, 100, '5m', False, False),
        (1200, 1200 - 450, 1000, 100, '5m', True, True),
        (1200, 1200 - 300, 1000, 10, '5m', True, False),
        (1200, None, 1200 - 300, 10, '5m', True, False),
        (1200, None, 1200 - 310, 10, '5m', True, True),
        (1800, None, 1800 - 1300, 300, '5m', True, True),
        (3900, None, 3900 - 400, 50, '1h', True, True),
        (900, 300, 900, 300, '5m', True, True),
        (7600, 3600, 4500, 200, '1h', True, True),
        (7600, 3600, 4500, 401, '1h', True, False),
    ]
)
def test_should_send_watermark(now, watermark, offset, watermark_delay, bucket_size, uses_schema, er):
    pipeline_ = Mock()
    pipeline_.uses_schema = Mock(return_value=uses_schema)
    pipeline_.watermark_delay = watermark_delay
    pipeline_.periodic_watermark_config = {'bucket_size': bucket_size}
    pipeline_.has_periodic_watermark_config = Mock(return_value=True)
    pipeline.manager.is_running = Mock(return_value=True)

    if watermark:
        pipeline_.watermark = Mock()
        pipeline_.watermark.timestamp = watermark
        pipeline_.has_watermark = Mock(return_value=True)
    else:
        pipeline_.watermark = None
        pipeline_.has_watermark = Mock(return_value=False)

    if offset:
        pipeline_.offset = Mock()
        pipeline_.offset.timestamp = offset
        pipeline_.has_offset = Mock(return_value=True)
    else:
        pipeline_.offset = None
        pipeline_.has_offset = Mock(return_value=False)

    watermark_manager = pipeline.manager.PeriodicWatermarkManager(pipeline_)
    watermark_manager._get_local_now_timestamp = Mock(return_value=now)
    assert watermark_manager.should_send_watermark() == er


def test_should_not_send_watermark():
    pipeline_ = Mock()
    pipeline_.uses_schema = Mock(return_value=True)
    pipeline.manager.is_running = Mock(return_value=True)
    pipeline_.has_offset = Mock(return_value=True)
    pipeline_.periodic_watermark_config = {}
    pipeline_.has_periodic_watermark_config = Mock(return_value=False)

    assert pipeline.manager.PeriodicWatermarkManager(pipeline_).should_send_watermark() is False

#
@pytest.mark.parametrize(
    "now, watermark, offset, watermark_delay, bucket_size, er", [
        (70, None, 35, 10, '1m', 60),
        (650, 540, 580, 10, '1m', 600),
        (650, 300, 330, 10, '1m', 600),
        (650, None, 330, 10, '1m', 600),
        (1250, 900, 930, 50, '5m', 1200),
        (1250, 600, 630, 50, '5m', 1200),
        (1250, None, 930, 50, '5m', 1200),
        (1250, None, 630, 50, '5m', 1200),
        (7250, 3600, 3930, 50, '1h', 7200),
        (10860, 3600, 3930, 50, '1h', 10800),
        (7250, None, 3930, 50, '1h', 7200),
        (7250, None, 630, 50, '1h', 7200),
        (86600, None, 10000, 100, '1d', 86400),
        (173000, 86400, 100000, 100, '1d', 172800),
    ]
)
def test_calculate_watermark(now, watermark, offset, watermark_delay, bucket_size, er):
    pipeline_ = Mock()
    pipeline_.watermark_delay = watermark_delay
    pipeline_.periodic_watermark_config = {'bucket_size': bucket_size}

    if watermark:
        pipeline_.watermark = Mock()
        pipeline_.watermark.timestamp = watermark
        pipeline_.has_watermark = Mock(return_value=True)
    else:
        pipeline_.watermark = None
        pipeline_.has_watermark = Mock(return_value=False)

    if offset:
        pipeline_.offset = Mock()
        pipeline_.offset.timestamp = offset
    else:
        pipeline_.offset = None

    watermark_manager = pipeline.manager.PeriodicWatermarkManager(pipeline_)
    watermark_manager._get_local_now_timestamp = Mock(return_value=now)
    assert watermark_manager.get_latest_bucket_start() == er


def test_calculate_timezone_watermark():
    tz_name = 'Etc/GMT-1'
    tz = pytz.timezone(tz_name)
    now = datetime.utcnow()

    pipeline_ = Mock()
    pipeline_.watermark_delay = 1
    pipeline_.periodic_watermark_config = {'bucket_size': '1h', 'timezone': tz_name}
    pipeline_.watermark = None
    pipeline_.offset = Mock()
    pipeline_.offset.timestamp = (now - tz.utcoffset(now)).timestamp()

    ar = pipeline.manager.PeriodicWatermarkManager(pipeline_).get_latest_bucket_start()
    er = int((now.replace(minute=0, second=0, microsecond=0) - tz.utcoffset(now) + timedelta(hours=1)).timestamp())
    assert ar == er
    # it should be equal 0 because bucket size is 1h and timezone is Etc/GMT-1 which is 1 hour ahead of UTC
    assert datetime.fromtimestamp(ar).hour - now.hour == 0

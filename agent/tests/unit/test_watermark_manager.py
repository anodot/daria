import pytest

from unittest.mock import Mock
from agent import pipeline


@pytest.mark.parametrize(
    "now, watermark, offset, watermark_delay, bucket_size, uses_schema, er", [
        # todo add column created at, don't specify nullable false
        # todo should send if pipeline is running and offset updated at < now - bucket_size
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
    pipeline_.uses_schema = uses_schema
    pipeline_.watermark_delay = watermark_delay
    pipeline_.periodic_watermark_config = {'bucket_size': bucket_size}
    pipeline.manager.time.time = Mock(return_value=now)

    if watermark:
        pipeline_.watermark = Mock()
        pipeline_.watermark.timestamp = watermark
    else:
        pipeline_.watermark = None

    if offset:
        pipeline_.offset = Mock()
        pipeline_.offset.offset = offset
    else:
        pipeline_.offset = None

    assert pipeline.manager.PeriodicWatermarkManager().should_send_watermark(pipeline_) == er


def test_should_not_send_watermark():
    pipeline_ = Mock()
    pipeline_.uses_schema = True
    pipeline_.periodic_watermark_config = None

    assert pipeline.manager.PeriodicWatermarkManager().should_send_watermark(pipeline_) is False


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
    pipeline.manager.time.time = Mock(return_value=now)

    if watermark:
        pipeline_.watermark = Mock()
        pipeline_.watermark.timestamp = watermark
    else:
        pipeline_.watermark = None

    if offset:
        pipeline_.offset = Mock()
        pipeline_.offset.offset = offset
    else:
        pipeline_.offset = None

    res = pipeline.manager.PeriodicWatermarkManager().get_latest_bucket_start(pipeline_)
    assert res == er

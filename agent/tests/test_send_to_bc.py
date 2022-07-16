import os
import subprocess

from datetime import datetime

import pytest

from agent.scripts.send_to_bc import (
    _get_notification_for_pipeline, ErrorNotification,
    PIPLINE_NO_DATA_ERROR_CODE, GENERAL_PIPELINE_ERROR_CODE,
)
from agent.pipeline import pipeline


def test_send_to_bc():
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'send_to_bc.py')
    try:
        subprocess.check_output(['python', path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise


def test_send_no_data_notification_condition_for_pipeline_without_notifications(test_pipeline: pipeline.TestPipeline):
    test_pipeline.notifications = None
    assert pipeline.manager.should_send_no_data_error_notification(test_pipeline) is False


@pytest.mark.parametrize('params, expected_result', [
    # Case: watermark was created 2 hours ago, notify period 1h, no_data notify wasn't sent
    ({}, True),
    # Case: watermark timestamp == now
    ({"watermark_timestamp": datetime.now().timestamp()}, False),
    # Case: no data notification was sent 30 minutes ago
    ({"watermark_timestamp": datetime.now().timestamp() - 1800}, False),
    # Case: no data notification was sent
    ({'no_data_notification_sent': True}, False),
    # Case: notifications is disabled
    ({'error_notification_enabled': False}, False),
])
def test_send_no_data_notification_condition(pipeline_builder, params, expected_result):
    assert pipeline.manager.should_send_no_data_error_notification(pipeline_builder(**params)) == expected_result


def test_send_no_data_notification_condition_for_pipeline_without_retries(test_pipeline: pipeline.TestPipeline):
    test_pipeline.retries = None
    assert pipeline.manager.should_send_retries_error_notification(test_pipeline) is False


@pytest.mark.parametrize('params, expected_result', [
    # Case: watermark was created 2 hours ago, notify period 1h, retries notify wasn't sent
    ({}, True),
    # Case: retries notification was sent
    ({'retries_notification_sent': True}, False),
    # Case: notifications is disabled
    ({'error_notification_enabled': False}, False),
    # Case: got 2 error statuses
    ({'retries_error_statuses': 2}, False),
])
def test_send_retries_error_notification_condition(pipeline_builder, params, expected_result):
    assert pipeline.manager.should_send_retries_error_notification(pipeline_builder(**params)) == expected_result


@pytest.mark.parametrize('params, expected_result', [
    ({'retries_notification_sent': False}, ErrorNotification(GENERAL_PIPELINE_ERROR_CODE, 'pipeline error')),
    ({'retries_notification_sent': True}, ErrorNotification(PIPLINE_NO_DATA_ERROR_CODE, 'No data for at least 1 hours')),
    ({'retries_notification_sent': True, 'no_data_notification_sent': True}, None),
    ({'no_data_notification_sent': True}, ErrorNotification(GENERAL_PIPELINE_ERROR_CODE, 'pipeline error')),
])
def test_get_notification_for_pipeline(pipeline_builder, params, expected_result):
    assert _get_notification_for_pipeline(pipeline_builder(**params)) == expected_result

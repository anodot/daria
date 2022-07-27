from datetime import datetime, timedelta
import os
import subprocess
import pytest
from unittest.mock import patch

from agent.scripts.reset_retry_counters import _reset_notifications, _reset_retries

def test_reset_retry_counters():
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'reset_retry_counters.py')
    try:
        subprocess.check_output(['python', path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise


@pytest.mark.parametrize('params, expected_value', [
    ({}, False),
    ({'retries_last_updated': datetime.now() - timedelta(hours=2)}, False),
    ({'retries_last_updated': datetime.now() - timedelta(minutes=30)}, True),
])
@patch('agent.pipeline.repository.save')
def test_reset_retries(save_mock, pipeline_builder, params, expected_value):
    save_mock = lambda x: None
    pipeline_ = pipeline_builder(retries_notification_sent=True, **params)
    _reset_retries(pipeline_)
    assert pipeline_.retries.notification_sent == expected_value


@pytest.mark.parametrize('params, expected_value', [
    ({}, False),
    ({'no_data_last_updated': datetime.now() - timedelta(hours=2)}, False),
    ({'no_data_last_updated': datetime.now() - timedelta(minutes=30)}, True),
])
@patch('agent.pipeline.repository.save')
def test_reset_notifications(save_mock, pipeline_builder, params, expected_value):
    save_mock = lambda x: None
    pipeline_ = pipeline_builder(no_data_notification_sent=True, **params)
    _reset_notifications(pipeline_)
    assert pipeline_.notifications.no_data_notification.notification_sent == expected_value


def test_reset_pipeline_without_notifications(test_pipeline):
    test_pipeline.notifications.no_data_notification = None
    assert _reset_notifications(test_pipeline) is None
    test_pipeline.notifications = None
    assert _reset_notifications(test_pipeline) is None


def test_reset_pipeline_without_retries(test_pipeline):
    test_pipeline.retries = None
    assert _reset_retries(test_pipeline) is None

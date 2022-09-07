import json
import os
import pytest
import requests
import aiohttp

from unittest.mock import Mock, MagicMock
from datetime import datetime
from random import randint
from click.testing import CliRunner
from agent import di
from agent.api import main
from agent.pipeline.pipeline import TestPipeline, PipelineWatermark, PipelineRetries, PipelineOffset
from agent.pipeline.notifications import NoDataNotifications, PiplineNotifications
from agent.modules import constants
from sdc_client import IPipelineProvider


DUMMY_DESTINATION_OUTPUT_PATH = '/output'
TEST_DATASETS_PATH = '/home/test-datasets'

INPUT_FILES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input_files')


@pytest.fixture(scope="session")
def cli_runner():
    di.init()
    yield CliRunner()


@pytest.fixture
def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        yield client


def get_output(file_name) -> list:
    for filename in os.listdir(DUMMY_DESTINATION_OUTPUT_PATH):
        if filename == file_name:
            with open(os.path.join(DUMMY_DESTINATION_OUTPUT_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(INPUT_FILES_DIR, f'{name}')


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.cls is None or not hasattr(metafunc.cls, 'params') or metafunc.function.__name__ not in metafunc.cls.params:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    function_argnames = set(metafunc.function.__code__.co_varnames[:metafunc.function.__code__.co_argcount])
    params = sorted(list(function_argnames - {'self', 'cli_runner', 'api_client'}))
    metafunc.parametrize(params, [[funcargs.get(name, None) for name in params] for funcargs in funcarglist])


def generate_input(input_: dict) -> str:
    return '\n'.join(map(
        lambda x: str(x),
        input_.values()
    ))


@pytest.fixture
def test_pipeline() -> TestPipeline:
    source_ = Mock()
    source_.type = 'some_type'
    pipeline_: TestPipeline = Mock(spec=TestPipeline)
    pipeline_.source = source_
    pipeline_.notifications = PiplineNotifications(
        pipeline_id=pipeline_.name,
        no_data_notification=NoDataNotifications(
            pipeline_=pipeline_,
            notification_period="60m",
            dvp_notification_period="24h"
        )
    )
    pipeline_.watermark = PipelineWatermark(
        pipeline_id=pipeline_.name,
        timestamp=int(datetime.now().timestamp())
    )
    pipeline_.offset = PipelineOffset(
        pipeline_id=pipeline_.name,
        timestamp=int(datetime.now().timestamp()),
        offset='offset'
    )
    pipeline_.retries = PipelineRetries(
        pipeline_=pipeline_,
    )
    pipeline_.dvp_config = {}
    pipeline_.interval = 60
    return pipeline_


@pytest.fixture
def pipeline_builder(test_pipeline: TestPipeline):
    def builder(
        no_data_notification_period=60,
        no_data_notification_sent=False,
        watermark_timestamp=datetime.now().timestamp() - 7200,
        offset_timestamp=datetime.now().timestamp() - 7200,
        error_notification_enabled=True,
        retries_error_statuses=constants.STREAMSETS_NOTIFY_AFTER_RETRY_ATTEMPTS + 1,
        retries_notification_sent=False,
        retries_last_updated=None,
        no_data_last_updated=None,
        dvp_config={},
    ):
        test_pipeline.notifications.no_data_notification.notification_period = no_data_notification_period
        test_pipeline.notifications.no_data_notification.notification_sent = no_data_notification_sent
        test_pipeline.notifications.no_data_notification.last_updated = no_data_last_updated
        test_pipeline.watermark.timestamp = watermark_timestamp
        test_pipeline.offset.timestamp = offset_timestamp
        test_pipeline.error_notification_enabled = lambda: error_notification_enabled
        test_pipeline.retries.number_of_error_statuses = retries_error_statuses
        test_pipeline.retries.notification_sent = retries_notification_sent
        test_pipeline.retries.last_updated = retries_last_updated
        test_pipeline.dvp_config = dvp_config
        return test_pipeline
    return builder


class PipelineMock:
    def __init__(self, type_: str = None):
        self.type_ = type_
        self.id = randint(0, 1000)

    def get_id(self):
        return self.id

    @staticmethod
    def set_streamsets(s):
        pass

    @staticmethod
    def get_streamsets():
        o = Mock()
        o.get_url = MagicMock(return_value='url')
        return o

    @property
    def source_type(self):
        return self.type_

    def __repr__(self):
        return f'PipelineMock({self.id}| type={self.type_})'


class StreamSetsMock:
    def __init__(self, type_: str = None):
        self.id = randint(0, 1000)
        self.type = type_

    @staticmethod
    def get_url():
        return 'url'

    @staticmethod
    def get_username():
        return 'admin'

    @staticmethod
    def get_password():
        return 'admin'

    # @staticmethod
    def get_id(self):
        return self.id

    def get_preferred_type(self) -> str:
        return self.type

    def __repr__(self):
        return f'StreamsetsMock({self.id}| type={self.type})'


class MockAsyncResponse:
    def __init__(self, _text, status_code):
        self._text = _text
        self.status = status_code

    async def text(self):
        return self._text

    async def json(self, content_type=None):
        return {'json': self._text}

    def raise_for_status(self):
        if self.status == 200:
            return None
        raise aiohttp.ClientResponseError(
            status=self.status,
            history=None,
            request_info=None,
        )

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class MockResponse:
    def __init__(self, _text, status_code):
        self._text = _text
        self.status_code = status_code

    @property
    def text(self):
        return self._text

    def json(self):
        return {'json': self._text}

    def raise_for_status(self):
        if self.status_code == 200:
            return None
        response = requests.Response()
        response.status_code = self.status_code
        response.raise_for_status()


def instance(type_: type):
    if type_ == IPipelineProvider:
        pipeline = PipelineMock()
        pipeline.get_streamsets = MagicMock(return_value=StreamSetsMock())
        res = [pipeline]
    else:
        streamsets = StreamSetsMock()
        res = [streamsets]
    mock = Mock()
    mock.get_all = MagicMock(return_value=res)
    return mock

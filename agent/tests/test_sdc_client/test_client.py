import unittest
import requests

from unittest.mock import MagicMock
from sdc_client import client
from sdc_client.base_api_client import UnauthorizedException
from .mocks import MockResponse, StreamSetsMock


class TestGetJMX(unittest.TestCase):
    def test_get_jmx_success(self):
        requests.Session.get = MagicMock(return_value=MockResponse(
            _text='data',
            status_code=200
        ))
        result = client.get_jmx(StreamSetsMock(), 'query_params_1')
        self.assertEqual(result, {'json': 'data'})

    def test_get_jmx_unauthorized(self):
        requests.Session.get = MagicMock(return_value=MockResponse(
            _text='data',
            status_code=401,
        ))
        with self.assertRaises(UnauthorizedException):
            client.get_jmx(StreamSetsMock(), 'query_params_1')


if __name__ == '__main__':
    unittest.main()

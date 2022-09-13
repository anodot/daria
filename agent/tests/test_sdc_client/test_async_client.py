import unittest
import aiohttp

from unittest.mock import AsyncMock
from sdc_client import async_client as client
from sdc_client.base_api_client import UnauthorizedException
from .mocks import MockAsyncResponse, StreamSetsMock


class TestGetJMXAsync(unittest.TestCase):
    def test_get_jmx_async_success(self):
        aiohttp.ClientSession.get = AsyncMock(return_value=MockAsyncResponse(
            _text='data',
            status_code=200
        ))
        queries = [
            (StreamSetsMock(), 'query_params_1',),
            (StreamSetsMock(), 'query_params_2',),
        ]
        result = client.get_jmxes_async(queries=queries)
        self.assertEqual(result, [{'json': 'data'}, {'json': 'data'}])

    def test_get_jmx_async_unauthorized(self):
        aiohttp.ClientSession.get = AsyncMock(return_value=MockAsyncResponse(
            _text='data',
            status_code=401,
        ))
        queries = [
            (StreamSetsMock(), 'query_params_1',),
            (StreamSetsMock(), 'query_params_2',),
        ]
        with self.assertRaises(UnauthorizedException):
            client.get_jmxes_async(queries=queries)


if __name__ == '__main__':
    unittest.main()

from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestDirectory:
    params = {}

    def test_delete(self, client):
        result = client.get('/pipelines/test_basic/info/10')
        test = 1
        # client.post('/pipelines/test_basic/start')

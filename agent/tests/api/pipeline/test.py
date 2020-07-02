from .. import client
from ...test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestDirectory:
    params = {}

    def test_delete(self, client):
        client.delete('/pipelines/m')

import pytest

from agent.api import main
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client


class TestSources:
    params = {
        'test_create': [
            {
                'source_type': 'influx',
                'name': 'influx',
                'url': 'http://localhost:8086',
                'username': 'admin',
                'password': 'admin',
                'database': 'test',
            }
        ]
    }

    def test_create(self, client, source_type, name, url, username, password, database):
        result = client.post('/sources', json=dict(
            type=source_type,
            name=name,
            url=url,
            username=username,
            password=password,
            database=database
        ))

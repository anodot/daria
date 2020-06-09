import os
import tempfile

import pytest

from agent.api import main


@pytest.fixture
def client():
    db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
    main.app.config['TESTING'] = True

    with main.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(main.app.config['DATABASE'])


def test_create(client):
    result = client.post('/destination', data=dict(
        destination_url='http://dummy_destination',
        data_collection_token='token',
        use_proxy='false',
        access_key='access_key',
        host_id='my_host'
    ))
    test = 1


def test_get(client):
    result = client.get('/destination')

import gzip
import os
import requests

from .. import conftest


def test_kafka_topology():
    file_type = 'test'
    res = requests.post('http://localhost/scripts/kafka_topology', json={
        'topic': 'test_kfk',
        'brokers': ['kafka:29092'],
        'file_type': file_type
    })
    res.raise_for_status()
    with gzip.open(os.path.join(conftest.DUMMY_DESTINATION_OUTPUT_PATH, f'topology_{file_type}.gz'), 'r') as f_out:
        with open(os.path.join(conftest.TEST_DATASETS_PATH, 'test_json_items'), 'r') as f_in:
            assert f_in.read() == f_out.read().decode()

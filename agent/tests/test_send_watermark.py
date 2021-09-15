import os
import subprocess

from .conftest import get_output
from .test_pipelines.test_zpipeline_base import get_schema_id


def test_send_watermark():
    # this test checks if watermark for test_csv_kafka is sent, it should run after test_pipelines
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'send_to_bc.py')
    try:
        subprocess.check_output(['python', path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print('Status: FAIL', exc.returncode, exc.output)
        raise
    schema_id = get_schema_id("test_csv")
    assert get_output(f'{schema_id}_watermark.json') == {"schemaId": schema_id, "watermark": 1512889500.0}

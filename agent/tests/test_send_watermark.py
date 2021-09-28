import os
import subprocess

from .conftest import get_output
from .test_pipelines.zbase import get_schema_id


def test_send_watermark():
    # this test checks if watermark for test_csv_kafka is sent, it should run after test_pipelines
    schema_id = get_schema_id("test_csv")
    assert get_output(f'{schema_id}_watermark.json') == {"schemaId": schema_id, "watermark": 1512889500.0}

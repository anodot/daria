import json
import os
import jsonschema

from agent import source, pipeline
from agent.streamsets_api_client import api_client
from agent.tools import if_validation_enabled


def validate_json(source_obj: source.Source):
    validation_schema_files = {
        source.TYPE_INFLUX: 'influx.json',
        source.TYPE_KAFKA: 'kafka.json',
        source.TYPE_MONGO: 'mongo.json',
        source.TYPE_MYSQL: 'jdbc.json',
        source.TYPE_POSTGRES: 'jdbc.json',
        source.TYPE_ELASTIC: 'elastic.json',
        source.TYPE_SPLUNK: 'tcp_server.json',
        source.TYPE_DIRECTORY: 'directory.json',
        source.TYPE_SAGE: 'sage.json',
        source.TYPE_MONITORING: 'Monitoring'
    }
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'json_schema_definitions', validation_schema_files[source_obj.type]
    )
    with open(file_path) as f:
        json_schema = json.load(f)
    jsonschema.validate(source_obj.config, json_schema)


# def validate(source_obj: source.Source):


@if_validation_enabled
def validate_connection(source_: source.Source):
    test_pipeline_name = pipeline.manager.create_test_pipeline(source_)
    try:
        validate_status = api_client.validate(test_pipeline_name)
        api_client.wait_for_preview(test_pipeline_name, validate_status['previewerId'])
    finally:
        api_client.delete_pipeline(test_pipeline_name)
    # todo
    print('Successfully connected to the source')
    return True

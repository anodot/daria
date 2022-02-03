from typing import Optional
from agent import destination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.pipeline import Pipeline


def build(pipeline: Pipeline) -> dict:
    schema_ = {
        'version': '1',
        'name': pipeline.name,
        'dimensions': pipeline.dimension_names,
        'measurements': _get_measurements(pipeline),
        'missingDimPolicy': {
            'action': 'fill',
            'fill': 'NULL'
        },
    }
    if pipeline.dvp_config:  # set dvpConfig in schema only if it set in pipeline config
        schema_['dvpConfig'] = pipeline.dvp_config
    if pipeline.get_schema_id():
        schema_['id'] = pipeline.get_schema_id()
    return schema_


def _get_measurements(pipeline: Pipeline) -> dict:
    measurements = {
        measurement_name: {
            'aggregation': _get_aggregation_type(target_type),
            'countBy': 'none',
        }
        for measurement_name, target_type in pipeline.measurement_names_with_target_types.items()
    }
    if pipeline.count_records:
        measurements[pipeline.count_records_measurement_name] = {
            'aggregation': 'sum',
            'countBy': 'none'
        }
    return measurements


def _get_aggregation_type(target_type: str) -> str:
    return 'sum' if target_type in [Pipeline.COUNTER, Pipeline.RUNNING_COUNTER] else 'average'


def equal(old_schema, new_schema) -> bool:
    return {key: val for key, val in old_schema.items() if key != 'id'} == new_schema


def create(schema: dict) -> dict:
    # created schema contains additional id field
    return AnodotApiClient(destination.repository.get()).create_schema(schema)['schema']


def update(schema: dict) -> dict:
    # deletes schema and recreates with the same id field
    delete(schema['id'])
    return AnodotApiClient(destination.repository.get()).update_schema(schema)['schema']


def search(pipeline_id: str) -> Optional[str]:
    for schema_ in AnodotApiClient(destination.repository.get()).get_schemas():
        if schema_['streamSchemaWrapper']['schema']['name'] == pipeline_id:
            return schema_['streamSchemaWrapper']['schema']['id']
    return None


def delete(schema_id: str):
    AnodotApiClient(destination.repository.get()).delete_schema(schema_id)

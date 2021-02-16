from typing import Optional
from agent import destination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.pipeline import Pipeline


def build(pipeline: Pipeline) -> dict:
    measurements = {}
    for idx, value in enumerate(pipeline.values):
        measurements[pipeline.measurement_names[idx]] = {
            'aggregation': 'sum' if pipeline.target_types[idx] == 'counter' else 'average',
            'countBy': 'none'
        }
    if pipeline.count_records:
        measurements[pipeline.count_records_measurement_name] = {
            'aggregation': 'sum',
            'countBy': 'none'
        }

    return {
        'version': '1',
        'name': pipeline.name,
        'dimensions': pipeline.dimensions_names + list(pipeline.constant_dimensions_names),
        'measurements': measurements,
        'missingDimPolicy': {
            'action': 'fill',
            'fill': 'NULL'
        }
    }


def equal(old_schema, new_schema) -> bool:
    return {key: val for key, val in old_schema.items() if key != 'id'} == new_schema


def create(schema: dict) -> dict:
    # created schema contains additional id field
    return AnodotApiClient(destination.repository.get()).create_schema(schema)['schema']


def search(pipeline_id: str) -> Optional[str]:
    for schema_ in AnodotApiClient(destination.repository.get()).get_schemas():
        if schema_['streamSchemaWrapper']['schema']['name'] == pipeline_id:
            return schema_['streamSchemaWrapper']['schema']['id']
    return None


def delete(schema_id: str):
    AnodotApiClient(destination.repository.get()).delete_schema(schema_id)

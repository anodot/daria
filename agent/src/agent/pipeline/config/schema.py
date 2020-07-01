from agent.anodot_api_client import AnodotApiClient
from agent import proxy
from agent.pipeline import Pipeline


def build(pipeline: Pipeline):
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
        'name': pipeline.id,
        'dimensions': pipeline.dimensions_names + list(pipeline.constant_dimensions_names),
        'measurements': measurements,
        'missingDimPolicy': {
            'action': 'fill',
            'fill': 'NULL'
        }
    }


def equal(old_schema, new_schema) -> bool:
    return {key: val for key, val in old_schema.items() if key != 'id'} == new_schema


def update(pipeline: Pipeline) -> dict:
    new_schema = build(pipeline)
    api_client = AnodotApiClient(pipeline.destination.access_key, proxy.get_config(pipeline.destination.proxy),
                                 base_url=pipeline.destination.url)

    old_schema = pipeline.get_schema()
    if old_schema:
        if equal(old_schema, new_schema):
            return old_schema
        api_client.delete_schema(pipeline.get_schema_id())

    created_schema = api_client.create_schema(new_schema)
    return created_schema

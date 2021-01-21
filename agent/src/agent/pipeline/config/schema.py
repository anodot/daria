from agent.destination import anodot_api_client
from agent.pipeline import Pipeline


def create(pipeline: Pipeline):
    api_client = anodot_api_client.AnodotApiClient(pipeline.destination)
    created_schema = api_client.create_schema(_build(pipeline))
    return created_schema['schema']


def update(pipeline: Pipeline) -> dict:
    if pipeline.has_schema():
        schema = _build(pipeline)
        api_client = anodot_api_client.AnodotApiClient(pipeline.destination)
        if _equal(pipeline.get_schema(), schema):
            return pipeline.get_schema()
        api_client.delete_schema(pipeline.get_schema_id())
        created_schema = api_client.create_schema(schema)
        return created_schema['schema']


def _build(pipeline: Pipeline) -> dict:
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


def _equal(old_schema, new_schema) -> bool:
    return {key: val for key, val in old_schema.items() if key != 'id'} == new_schema
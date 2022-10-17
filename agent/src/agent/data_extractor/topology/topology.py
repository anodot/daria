from abc import ABC
from agent.pipeline import Pipeline
from agent.modules import field, lookup

REGION = 'REGION'
SITE = 'SITE'
NODE = 'NODE'
CARD = 'CARD'
INTERFACE = 'INTERFACE'
CELL = 'CELL'
LINK = 'LINK'
SERVICE = 'SERVICE'
LOGICAL_GROUP = 'LOGICAL_GROUP'
APPLICATION = 'APPLICATION'

ENTITIES = [REGION, SITE, NODE, CARD, INTERFACE, CELL, LINK, SERVICE, LOGICAL_GROUP, APPLICATION]


def transform_metrics(pipeline_: Pipeline, data: dict) -> dict:
    with lookup.Provide(pipeline_.lookups):
        entities = _create_entities(pipeline_)
        return _create_topology_records(entities, data)


class Entity(ABC):
    def __init__(self, name: str, config: dict):
        self.name: str = name
        self.fields: list[field.Field] = field.build_fields(config)


def _create_topology_records(entities: list[Entity], data: dict) -> dict:
    records = {}
    for entity_ in entities:
        new_records = [field.extract_fields(entity_.fields, row) for row in data]
        if entity_.name in records:
            records[entity_.name].extend(new_records)
        else:
            records[entity_.name] = new_records
    return records


def _create_entities(pipeline_: Pipeline) -> list[Entity]:
    return [Entity(entity['type'].upper(), entity['mapping']) for entity in pipeline_.config['entity']]

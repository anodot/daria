from abc import ABC
from agent.pipeline import Pipeline
from agent.modules import field, lookup

REGION = 'REGION'
SUBREGION = 'SUBREGION'
SITE = 'SITE'
NODE = 'NODE'
CARD = 'CARD'
INTERFACE = 'INTERFACE'
CELL = 'CELL'
LINK = 'LINK'
SERVICE = 'SERVICE'
LOGICAL_GROUP = 'LOGICAL_GROUP'
APPLICATION = 'APPLICATION'

ENTITIES = [REGION, SUBREGION, SITE, NODE, CARD, INTERFACE, CELL, LINK, SERVICE, LOGICAL_GROUP, APPLICATION]


def transform_metrics(pipeline_: Pipeline, data: dict) -> dict:
    with lookup.Provide(pipeline_.lookups):
        entities = _create_entities(pipeline_)
        return _create_topology_records(entities, data)


class Entity(ABC):
    def __init__(self, name: str, config: dict):
        self.name: str = name
        self.fields: list[field.Field] = field.build_fields(config)


def _create_topology_records(entities: list[Entity], data: dict) -> dict:
    records = {
        entity_.name: [field.extract_fields(entity_.fields, row) for row in data]
        for entity_ in entities
    }
    if SUBREGION in records:
        records = _merge_subregion_to_region(records)
        del records[SUBREGION]
    return records


def _create_entities(pipeline_: Pipeline) -> list[Entity]:
    return [Entity(name.upper(), entity_config) for name, entity_config in pipeline_.config['entity'].items()]


def _merge_subregion_to_region(records: dict[ENTITIES, dict]) -> dict[ENTITIES, dict]:
    if REGION not in records:
        records[REGION] = records[SUBREGION]
    else:
        records[REGION].extend(records[SUBREGION])
    return records

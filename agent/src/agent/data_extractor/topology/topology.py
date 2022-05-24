from abc import ABC
from agent.modules.data_source import DataSource
from agent.pipeline import Pipeline
from agent.source import Source
from agent.modules import field, data_source, lookup

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

TOPOLOGY_ENTITIES = [REGION, SITE, NODE, CARD, INTERFACE, CELL, LINK, SERVICE, LOGICAL_GROUP, APPLICATION]

# todo add jsonschema definition for topology, now it's almost empty
# todo change /usr/src/app dir to /home

def extract_metrics(pipeline_: Pipeline) -> dict:
    with lookup.Provide(pipeline_.lookups):
        entities = _create_entities(pipeline_.source)
        return _create_topology_records(entities)


class Entity(ABC):
    def __init__(self, name: str, config: dict):
        self.name: str = name
        self.source: DataSource = data_source.build(config['source'])
        self.fields: list[field.Field] = field.build_fields(config['fields'])


def _create_topology_records(entities: list[Entity]) -> dict:
    return {
        entity_.name: [field.extract_fields(entity_.fields, row) for row in entity_.source.get_data()]
        for entity_ in entities
    }


def _create_entities(source_: Source) -> list[Entity]:
    return [Entity(name.upper(), entity_config) for name, entity_config in source_.config['entities'].items()]

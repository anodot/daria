from abc import ABC
from agent.modules.data_source import DataSource
from agent.pipeline import Pipeline
from agent.source import Source
from agent.modules import field, data_source, lookup

REGION = 'region'
SITE = 'site'
NODE = 'node'
CARD = 'card'
INTERFACE = 'interface'
CELL = 'cell'
LINK = 'link'
SERVICE = 'service'
LOGICAL_GROUP = 'logical_group'
APPLICATION = 'application'

TOPOLOGY_ENTITIES = [REGION, SITE, NODE, CARD, INTERFACE, CELL, LINK, SERVICE, LOGICAL_GROUP, APPLICATION]

# todo add username/password/token/whatever to the agent/source/sensitive_data.py
# todo add jsonschema definition for topology, now it's almost empty


def extract_metrics(pipeline_: Pipeline) -> dict:
    with lookup.Provide(pipeline_.lookup):
        entities = _create_entities(pipeline_.source)
        topology_records = _create_topology_records(entities)
        return _build_topology_data(topology_records)


class Entity(ABC):
    def __init__(self, name: str, config: dict):
        self.name: str = name
        # todo if one source can contain multiple entities then they must be separate
        self.source: DataSource = data_source.build(config['source'])
        self.fields: list[field.Field] = field.build_fields(config['fields'])


def _create_topology_records(entities: list[Entity]) -> list:
    records = []
    for entity_ in entities:
        for row in entity_.source.get_data():
            records.append(field.extract_fields(entity_.fields, row))
    return records


def _build_topology_data(topology_entities: list) -> dict:
    pass


def _create_entities(source_: Source) -> list[Entity]:
    return [Entity(name, entity_config) for name, entity_config in source_.config['entities'].items()]

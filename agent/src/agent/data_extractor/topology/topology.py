from abc import ABC
from agent.pipeline import Pipeline
from agent.source import Source
from agent.data_extractor.topology import lookup, field, entity

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


def extract_metrics(pipeline_: Pipeline) -> dict:
    lookup.init_sources(pipeline_.source.config.get('lookup', {}))
    entities = _create_entities(pipeline_.source)
    topology_records = _create_topology_records(entities)
    topology_data = _build_topology_data(topology_records)
    lookup.clean_cache()
    return topology_data


class Entity(ABC):
    def __init__(self, name: str, config: dict):
        self.name: str = name
        # todo if one source can contain multiple entities then they must be separate
        self.source: entity.Source = entity.source.build(config['source'])
        self.fields: list[field.Field] = field.build_fields(config['fields'])


def _create_topology_records(entities: list[Entity]) -> list:
    records = []
    for entity_ in entities:
        for row in entity_.source.get_data():
            record = {}
            for field_ in entity_.fields:
                value = field.extract(row, field_)
                for transformer in field_.get_transformers():
                    value = transformer.transform(value)
                record[field_.get_name()] = value
            records.append(record)
    return records


def _build_topology_data(topology_entities: list) -> dict:
    pass


def _create_entities(source_: Source) -> list[Entity]:
    return [Entity(name, entity_config) for name, entity_config in source_.config['entities'].items()]

from typing import List

from agent.db import Session, entity
from agent import source
from agent.constants import MONITORING_SOURCE_NAME
from jsonschema import ValidationError

session = Session()


def exists(source_name: str) -> bool:
    return session.query(
        session.query(entity.Source).filter(entity.Source.name == source_name).exists()
    ).scalar()


def update(source_: source.Source):
    source_entity = _get_entity(source_.name)
    source_entity.name = source_.name
    source_entity.type = source_.type
    source_entity.config = source_.config
    session.commit()


def create(source_: source.Source):
    if exists(source_.name):
        raise source.SourceException(f"Source {source_.name} already exists")
    session.add(source_.to_entity())
    session.commit()


def delete_by_name(source_name: str):
    if not exists(source_name):
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    source_entity = session.query(entity.Source).filter(entity.Source.name == source_name).first()
    if source_entity.pipelines:
        raise Exception(
                f"Can't delete. Source is used by {', '.join([p.name for p in source_entity.pipelines])} pipelines"
            )
    session.delete(source_entity)
    session.commit()


def get_all_names() -> List[str]:
    return list(map(
        lambda row: row[0],
        session.query(entity.Source.name).all()
    ))


def find_by_name_beginning(name_part: str) -> List:
    return session.query(entity.Source).filter(entity.Source.name.like(f'{name_part}%')).all()


def get(source_id: int) -> source.Source:
    source_entity = session.query(entity.Source).get(source_id)
    if not source_entity:
        raise SourceNotExists(f"Source ID = {source_id} doesn't exist")
    return _construct_source(source_entity)


def get_by_name(source_name: str) -> source.Source:
    # if source_name == MONITORING_SOURCE_NAME:
    #     return source.MonitoringSource(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {})
    return _construct_source(_get_entity(source_name))


def _construct_source(source_entity: entity.Source) -> source.Source:
    source_ = source.manager.create_source_obj(source_entity.name, source_entity.type)
    source_.config = source_entity.config
    source_.id = source_entity.id
    # todo do we need this validation?
    try:
        source.validator.get_validator(source_).validate_json()
    except ValidationError:
        raise SourceConfigDeprecated(f'Config for source {source_entity.name} is not supported. Please recreate the source')
    return source_


def _get_entity(source_name: str) -> entity.Source:
    source_entity = session.query(entity.Source).filter(entity.Source.name == source_name).first()
    if not source_entity:
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    return source_entity


class SourceNotExists(Exception):
    pass


class SourceConfigDeprecated(Exception):
    pass

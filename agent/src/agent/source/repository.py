from typing import List
from agent import source
from agent.db import Session

session = Session()


def exists(source_name: str) -> bool:
    res = session.query(
        session.query(source.Source).filter(source.Source.name == source_name).exists()
    ).scalar()
    return res


def save(source_: source.Source):
    session.add(source_)
    session.commit()


def delete_by_name(source_name: str):
    if not exists(source_name):
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    source_entity = session.query(source.Source).filter(source.Source.name == source_name).first()
    if source_entity.pipelines:
        raise Exception(
                f"Can't delete. Source is used by {', '.join([p.name for p in source_entity.pipelines])} pipelines"
            )
    session.delete(source_entity)
    session.commit()


def get_all_names() -> List[str]:
    res = list(map(
        lambda row: row[0],
        session.query(source.Source.name).all()
    ))
    return res


def find_by_name_beginning(name_part: str) -> List:
    res = session.query(source.Source).filter(source.Source.name.like(f'{name_part}%')).all()
    return res


def get(source_id: int) -> source.Source:
    source_ = session.query(source.Source).get(source_id)
    if not source_:
        raise SourceNotExists(f"Source ID = {source_id} doesn't exist")
    res = _construct_source(source_)
    return res


def get_by_name(source_name: str) -> source.Source:
    source_ = session.query(source.Source).filter(source.Source.name == source_name).first()
    if not source_:
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    res = _construct_source(source_)
    return res


def _construct_source(source_: source.Source) -> source.Source:
    source_.__class__ = source.types[source_.type]
    source_.sample_data = None
    return source_


class SourceNotExists(Exception):
    pass


class SourceConfigDeprecated(Exception):
    pass

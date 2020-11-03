from typing import List, Optional
from agent import source
from agent.modules.db import session
from agent.source import Source


def exists(source_name: str) -> bool:
    res = session().query(
        session().query(Source).filter(Source.name == source_name).exists()
    ).scalar()
    return res


def save(source_: Source):
    session().add(source_)
    session().commit()


def delete(source_: Source):
    if source_.pipelines:
        raise Exception(
                f"Can't delete. Source is used by {', '.join([p.name for p in source_.pipelines])} pipelines"
            )
    session().delete(source_)
    session().commit()


def delete_by_name(source_name: str):
    delete(get_by_name(source_name))


def get_all_names() -> List[str]:
    res = list(map(
        lambda row: row[0],
        session().query(Source.name).all()
    ))
    return res


def find_by_name_beginning(name_part: str) -> List:
    res = session().query(Source).filter(Source.name.like(f'{name_part}%')).all()
    return res


def get(source_id: int) -> Source:
    source_ = session().query(Source).get(source_id)
    if not source_:
        raise SourceNotExists(f"Source ID = {source_id} doesn't exist")
    res = _construct_source(source_)
    return res


def get_by_name(source_name: str) -> Source:
    source_ = session().query(Source).filter(Source.name == source_name).first()
    if not source_:
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    res = _construct_source(source_)
    return res


def _construct_source(source_: Source) -> Source:
    source_.__class__ = source.types[source_.type]
    return source_


def get_all() -> List[Source]:
    return session().query(Source).all()


def get_last_edited(source_type: str) -> Optional[Source]:
    return session().query(Source).filter(Source.type == source_type).order_by(Source.last_edited.desc()).first()


class SourceNotExists(Exception):
    pass

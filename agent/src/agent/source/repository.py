from functools import wraps
from typing import List, Optional
from agent import source
from agent.modules.db import Session
from agent.source import Source


def typed_source(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, list):
            return [_construct_source(source_) for source_ in res]
        else:
            if res is not None:
                return _construct_source(res)
            else:
                return res
    return wrapper


def exists(source_name: str) -> bool:
    return Session.query(
        Session.query(Source).filter(Source.name == source_name).exists()
    ).scalar()


def save(source_: Source):
    if not Session.object_session(source_):
        Session.add(source_)
    Session.commit()


def delete(source_: Source):
    if source_.pipelines:
        raise Exception(
                f"Can't delete. Source is used by {', '.join([p.name for p in source_.pipelines])} pipelines"
            )
    Session.delete(source_)
    Session.commit()


def delete_by_name(source_name: str):
    delete(get_by_name(source_name))


def get_all_names() -> List[str]:
    return list(map(
        lambda row: row[0],
        Session.query(Source.name).all()
    ))


@typed_source
def find_by_name_beginning(name_part: str) -> List[Source]:
    return Session.query(Source).filter(Source.name.like(f'{name_part}%')).all()


@typed_source
def get(source_id: int) -> Source:
    source_ = Session.query(Source).get(source_id)
    if not source_:
        raise SourceNotExists(f"Source ID = {source_id} doesn't exist")
    return source_


@typed_source
def get_by_name(source_name: str) -> Source:
    source_ = Session.query(Source).filter(Source.name == source_name).first()
    if not source_:
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    return source_


@typed_source
def get_all() -> List[Source]:
    return Session.query(Source).all()


@typed_source
def get_last_edited(source_type: str) -> Optional[Source]:
    return Session.query(Source).filter(Source.type == source_type).order_by(Source.last_edited.desc()).first()


def _construct_source(source_: Source) -> Source:
    source_.__class__ = source.types[source_.type]
    return source_


class SourceNotExists(Exception):
    pass

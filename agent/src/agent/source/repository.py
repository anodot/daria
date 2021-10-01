from functools import wraps
from typing import List, Optional
from agent.modules.db import Session, engine
from agent.source import Source, make_typed
from sqlalchemy.orm import Query


def typed_source(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, list):
            return [make_typed(source_) for source_ in res]
        else:
            if res is not None:
                return make_typed(res)
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
def get_by_type(source_type: str) -> List[Source]:
    return Session.query(Source).filter(Source.type == source_type).all()


@typed_source
def get_all() -> List[Source]:
    return Session.query(Source).all()


@typed_source
def get_last_edited(source_type: str) -> Optional[Source]:
    return Session.query(Source).filter(Source.type == source_type).order_by(Source.last_edited.desc()).first()


def get_by_name_without_session(source_name: str) -> Source:
    query_result = engine.execute(Query(Source).filter(Source.name == source_name).statement)

    sources = [i for i in query_result]
    if not sources:
        raise SourceNotExists

    return sources[0]


def is_modified(source_: Source) -> bool:
    return get_by_name_without_session(source_.name).config != source_.config


class SourceNotExists(Exception):
    pass

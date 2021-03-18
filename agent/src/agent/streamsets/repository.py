from typing import List
from agent.modules.db import Session
from agent.streamsets import StreamSets


def get(id_: int) -> StreamSets:
    streamsets = Session.query(StreamSets).filter(StreamSets.id == id_).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f'StreamSets with id {id_} doesn\'t exist')
    return streamsets


def get_all() -> List[StreamSets]:
    return Session.query(StreamSets).all()


def get_by_url(url: str) -> StreamSets:
    streamsets = Session.query(StreamSets).filter(StreamSets.url == url).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f'StreamSets with url {url} doesn\'t exist')
    return streamsets


def save(streamsets: StreamSets):
    if not Session.object_session(streamsets):
        Session.add(streamsets)
    Session.commit()


def delete(streamsets: StreamSets):
    Session.delete(streamsets)
    Session.commit()


def get_all_names() -> List[str]:
    res = list(map(
        lambda row: row[0],
        Session.query(StreamSets.url).all()
    ))
    return res


def exists(url: str) -> bool:
    return bool(Session.query(
        Session.query(StreamSets).filter(StreamSets.url == url).exists()
    ).scalar())


class StreamsetsNotExistsException(Exception):
    pass

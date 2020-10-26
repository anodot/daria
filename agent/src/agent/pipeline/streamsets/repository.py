from typing import List

from agent.modules.db import session
from agent.pipeline.streamsets import StreamSets


def get(id_: int) -> StreamSets:
    streamsets = session().query(StreamSets).filter(StreamSets.id == id_).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f"StreamSets with id {id_} doesn't exist")
    return streamsets


def get_all() -> List[StreamSets]:
    return session().query(StreamSets).all()


def get_by_url(url: str) -> StreamSets:
    streamsets = session().query(StreamSets).filter(StreamSets.url == url).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f"StreamSets with url {url} doesn't exist")
    return streamsets


def get_any() -> StreamSets:
    return session().query(StreamSets).first()


def save(streamsets: StreamSets):
    session().add(streamsets)
    session().commit()


def delete_by_url(url: str):
    session().delete(get_by_url(url))
    session().commit()


class StreamsetsNotExistsException(Exception):
    pass

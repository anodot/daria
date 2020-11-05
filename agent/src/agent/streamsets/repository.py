from typing import List
from agent.modules.db import session
from agent.streamsets import StreamSets


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


def save(streamsets: StreamSets):
    session().add(streamsets)
    session().flush()


def delete(streamsets: StreamSets):
    session().delete(streamsets)
    session().flush()


class StreamsetsNotExistsException(Exception):
    pass

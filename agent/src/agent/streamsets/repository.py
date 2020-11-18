from typing import List
from agent.modules.db import session
from agent.streamsets import StreamSets


def get(id_: int) -> StreamSets:
    streamsets = session().query(StreamSets).filter(StreamSets.id == id_).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f'StreamSets with id {id_} doesn\'t exist')
    return streamsets


def get_all() -> List[StreamSets]:
    return session().query(StreamSets).all()


def get_by_url(url: str) -> StreamSets:
    streamsets = session().query(StreamSets).filter(StreamSets.url == url).first()
    if not streamsets:
        raise StreamsetsNotExistsException(f'StreamSets with url {url} doesn\'t exist')
    return streamsets


def save(streamsets: StreamSets):
    session().add(streamsets)
    session().commit()


def delete(streamsets: StreamSets):
    session().delete(streamsets)
    session().commit()


def get_all_names() -> List[str]:
    res = list(map(
        lambda row: row[0],
        session().query(StreamSets.url).all()
    ))
    return res


def exists(url: str) -> bool:
    return bool(session().query(
        session().query(StreamSets).filter(StreamSets.url == url).exists()
    ).scalar())


class StreamsetsNotExistsException(Exception):
    pass

from typing import List, Dict
from agent.modules.db import session
from agent.streamsets import StreamSets
from agent.pipeline import Pipeline
from sqlalchemy import func


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


def count_pipelines_by_streamsets() -> Dict[int, int]:
    """ Returns { streamsets_id: number_of_pipelines } """
    res = session().query(StreamSets.id, func.count(Pipeline.id)).outerjoin(StreamSets.pipelines).\
        group_by(StreamSets.id).all()
    return {streamsets_id: number for (streamsets_id, number) in res if streamsets_id is not None}


class StreamsetsNotExistsException(Exception):
    pass

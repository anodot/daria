from typing import List, Dict
from sqlalchemy import func
from agent import pipeline
from agent.modules.db import session
from agent.pipeline import PipelineOffset, Pipeline
from agent.streamsets import StreamSets


class PipelineNotExistsException(Exception):
    pass


def exists(pipeline_name: str) -> bool:
    return bool(session().query(
        session().query(Pipeline).filter(Pipeline.name == pipeline_name).exists()
    ).scalar())


def monitoring_exists() -> bool:
    return bool(session().query(
        session().query(Pipeline).filter(Pipeline.name.like(f'{pipeline.MONITORING}%')).exists()
    ).scalar())


def get_by_name(pipeline_name: str) -> Pipeline:
    pipeline_ = session().query(Pipeline).filter(Pipeline.name == pipeline_name).first()
    if not pipeline_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_name} doesn't exist")
    return pipeline_


def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[Pipeline]:
    return session().query(Pipeline).all()


def save(pipeline_: Pipeline):
    session().add(pipeline_)
    session().flush()


def delete(pipeline_: Pipeline):
    session().delete(pipeline_)
    session().flush()


def delete_by_name(pipeline_name: str):
    delete(get_by_name(pipeline_name))


def save_offset(pipeline_offset: PipelineOffset):
    session().add(pipeline_offset)
    session().flush()


def delete_offset(pipeline_offset: PipelineOffset):
    session().delete(pipeline_offset)
    session().flush()


def count_by_streamsets() -> Dict[int, int]:
    """ Returns { streamsets_id: number_of_pipelines } """
    res = session().query(Pipeline.streamsets_id, func.count(Pipeline.streamsets_id)).group_by(Pipeline.streamsets_id).all()
    return {streamsets_id: number for (streamsets_id, number) in res if streamsets_id is not None}


def get_by_streamsets_id(streamsets_id: int) -> List[Pipeline]:
    return session().query(Pipeline).filter(Pipeline.streamsets_id == streamsets_id).all()

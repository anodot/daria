from functools import wraps
from typing import List
from agent import source
from agent.modules.db import Session, engine
from agent.pipeline import PipelineOffset, Pipeline
from sqlalchemy.orm import Query


def typed_source(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, list):
            return [_construct_source(pipeline) for pipeline in res]
        else:
            return _construct_source(res)
    return wrapper


def exists(pipeline_id: str) -> bool:
    return bool(Session.query(
        Session.query(Pipeline).filter(Pipeline.name == pipeline_id).exists()
    ).scalar())


@typed_source
def get_by_id(pipeline_id: str) -> Pipeline:
    pipeline_ = Session.query(Pipeline).filter(Pipeline.name == pipeline_id).first()
    if not pipeline_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    return pipeline_


def get_by_id_without_session(pipeline_id: str) -> Pipeline:
    query_result = engine.execute(Query(Pipeline).filter(Pipeline.name == pipeline_id).statement)

    pipelines_ = [i for i in query_result]
    if not pipelines_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    return pipelines_[0]


def get_by_type(type_: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.type == type_, get_all()))


@typed_source
def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


@typed_source
def get_all() -> List[Pipeline]:
    return Session.query(Pipeline).all()


def save(pipeline_: Pipeline):
    if not Session.object_session(pipeline_):
        Session.add(pipeline_)
    Session.commit()


def delete(pipeline_: Pipeline):
    Session.delete(pipeline_)
    Session.commit()


def save_offset(pipeline_offset: PipelineOffset):
    if not Session.object_session(pipeline_offset):
        Session.add(pipeline_offset)
    Session.commit()


def delete_offset(pipeline_offset: PipelineOffset):
    Session.delete(pipeline_offset)
    Session.commit()


@typed_source
def get_by_streamsets_id(streamsets_id: int) -> List[Pipeline]:
    return Session.query(Pipeline).filter(Pipeline.streamsets_id == streamsets_id).all()


@typed_source
def get_by_streamsets_url(streamsets_url: str) -> List[Pipeline]:
    return Session.query(Pipeline).filter(Pipeline.streamsets.has(url=streamsets_url)).all()


def add_deleted_pipeline_id(pipeline_id: str):
    Session.execute(f"INSERT INTO deleted_pipelines VALUES ('{pipeline_id}') ON CONFLICT DO NOTHING")
    Session.commit()


def remove_deleted_pipeline_id(pipeline_id: str):
    Session.execute(f"DELETE FROM deleted_pipelines WHERE pipeline_id = '{pipeline_id}'")
    Session.commit()


def get_deleted_pipeline_ids() -> list:
    return Session.execute('SELECT * FROM deleted_pipelines')


def _construct_source(pipeline: Pipeline) -> Pipeline:
    pipeline.source.__class__ = source.types[pipeline.source.type]
    return pipeline


class PipelineNotExistsException(Exception):
    pass

from functools import wraps
from typing import List
from agent import source, pipeline
from agent.destination import HttpDestination
from agent.modules.db import Session, engine, Entity
from agent.pipeline import PipelineOffset, Pipeline, PipelineRetries
from sqlalchemy.orm import Query


def typed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, list):
            return [_construct(pipeline_) for pipeline_ in res]
        else:
            return _construct(res)
    return wrapper


def exists(pipeline_id: str) -> bool:
    return bool(Session.query(
        Session.query(Pipeline).filter(Pipeline.name == pipeline_id).exists()
    ).scalar())


@typed
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


@typed
def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


@typed
def get_all() -> List[Pipeline]:
    return Session.query(Pipeline).all()


def save(entity: Entity):
    if not Session.object_session(entity):
        Session.add(entity)
    Session.commit()


def delete(pipeline_: Pipeline):
    Session.delete(pipeline_)
    Session.commit()


def delete_offset(pipeline_offset: PipelineOffset):
    Session.delete(pipeline_offset)
    Session.commit()


@typed
def get_by_streamsets_id(streamsets_id: int) -> List[Pipeline]:
    return Session.query(Pipeline).filter(Pipeline.streamsets_id == streamsets_id).all()


@typed
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


def delete_pipeline_retries(pipeline_retries: PipelineRetries):
    Session.delete(pipeline_retries)
    Session.commit()


def _construct(pipeline_: Pipeline) -> Pipeline:
    if not pipeline_.destination:
        # this is needed for raw pipelines
        pipeline_.destination = HttpDestination()
    return _construct_pipeline(
        _construct_source(pipeline_)
    )


def _construct_source(pipeline_: Pipeline) -> Pipeline:
    pipeline_.source.__class__ = source.types[pipeline_.source.type]
    return pipeline_


def _construct_pipeline(pipeline_: Pipeline) -> Pipeline:
    pipeline_.__class__ = pipeline.TYPES[pipeline_.type]
    return pipeline_


class PipelineNotExistsException(Exception):
    pass


class SessionManager:
    def __init__(self, entity):
        self.entity = entity
        self.session = Session()
        if not self.session.object_session(self.entity):
            self.session.add(self.entity)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value:
            self.session.expunge(self.entity)
            return False
        self.session.commit()
        return True

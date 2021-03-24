from typing import List
from agent.modules.db import Session
from agent.pipeline import PipelineOffset, Pipeline


class PipelineNotExistsException(Exception):
    pass


def exists(pipeline_id: str) -> bool:
    return bool(Session.query(
        Session.query(Pipeline).filter(Pipeline.name == pipeline_id).exists()
    ).scalar())


def get_by_id(pipeline_id: str) -> Pipeline:
    pipeline_ = Session.query(Pipeline).filter(Pipeline.name == pipeline_id).first()
    if not pipeline_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    return pipeline_


def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


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


def get_by_streamsets_id(streamsets_id: int) -> List[Pipeline]:
    return Session.query(Pipeline).filter(Pipeline.streamsets_id == streamsets_id).all()


def add_deleted_pipeline_id(pipeline_id: str):
    Session.execute(f"INSERT INTO deleted_pipelines VALUES ('{pipeline_id}') ON CONFLICT DO NOTHING")
    Session.commit()


def remove_deleted_pipeline_id(pipeline_id: str):
    Session.execute(f"DELETE FROM deleted_pipelines WHERE pipeline_id = '{pipeline_id}'")
    Session.commit()


def get_deleted_pipeline_ids() -> list:
    return Session.execute('SELECT * FROM deleted_pipelines')

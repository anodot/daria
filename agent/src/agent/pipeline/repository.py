from typing import List
from agent.modules.db import session
from agent.pipeline import PipelineOffset, Pipeline


class PipelineNotExistsException(Exception):
    pass


def exists(pipeline_id: str) -> bool:
    return bool(session().query(
        session().query(Pipeline).filter(Pipeline.name == pipeline_id).exists()
    ).scalar())


def get_by_id(pipeline_id: str) -> Pipeline:
    pipeline_ = session().query(Pipeline).filter(Pipeline.name == pipeline_id).first()
    if not pipeline_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    return pipeline_


def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[Pipeline]:
    return session().query(Pipeline).all()


def save(pipeline_: Pipeline):
    session().add(pipeline_)
    session().commit()


def delete(pipeline_: Pipeline):
    session().delete(pipeline_)
    session().commit()


def save_offset(pipeline_offset: PipelineOffset):
    session().add(pipeline_offset)
    session().commit()


def delete_offset(pipeline_offset: PipelineOffset):
    session().delete(pipeline_offset)
    session().commit()


def get_by_streamsets_id(streamsets_id: int) -> List[Pipeline]:
    return session().query(Pipeline).filter(Pipeline.streamsets_id == streamsets_id).all()


def add_deleted_pipeline_id(pipeline_id: str):
    session().execute(f"INSERT INTO deleted_pipelines VALUES ('{pipeline_id}') ON CONFLICT DO NOTHING")
    session().commit()


def remove_deleted_pipeline_id(pipeline_id: str):
    session().execute(f"DELETE FROM deleted_pipelines WHERE pipeline_id = '{pipeline_id}'")
    session().commit()


def get_deleted_pipeline_ids() -> list:
    return session().execute('SELECT * FROM deleted_pipelines')

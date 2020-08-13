from agent.db import Session, entity
from agent import source
from agent import destination
from typing import List
from agent.pipeline import pipeline

session = Session()


class PipelineNotExistsException(Exception):
    pass


def exists(pipeline_name: str) -> bool:
    return session.query(
        session.query(entity.Pipeline).filter(entity.Pipeline.name == pipeline_name).exists()
    ).scalar()


def get_by_name(pipeline_name: str) -> pipeline.Pipeline:
    return _construct_pipeline(_get_entity(pipeline_name))


def get_by_source(source_name: str) -> List[pipeline.Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[pipeline.Pipeline]:
    pipelines = []
    for pipeline_entity in session.query(entity.Pipeline).all():
        pipelines.append(_construct_pipeline(pipeline_entity))
    return pipelines


def create(pipeline_: pipeline.Pipeline):
    session.add(pipeline_.to_entity())
    session.commit()


def update(pipeline_: pipeline.Pipeline):
    pipeline_entity = _get_entity(pipeline_.id)
    pipeline_entity.name = pipeline_.id
    pipeline_entity.source_id = pipeline_.source.id
    pipeline_entity.config = pipeline_.config
    session.commit()


def delete(pipeline_: pipeline.Pipeline):
    delete_by_name(pipeline_.name)


def delete_by_name(pipeline_name: str):
    pipeline_entity = session.query(entity.Pipeline).filter(entity.Pipeline.name == pipeline_name).first()
    if not pipeline_entity:
        raise PipelineNotExistsException(f"Pipeline {pipeline_name} doesn't exist")
    session.delete(pipeline_entity)
    session.commit()


def _construct_pipeline(pipeline_entity: entity.Pipeline) -> pipeline.Pipeline:
    source_ = source.repository.get(pipeline_entity.source_id)
    return pipeline.Pipeline(pipeline_entity.name, source_, pipeline_entity.config, destination.repository.get())


def _get_entity(pipeline_name: str) -> entity.Pipeline:
    pipeline_entity = session.query(entity.Pipeline).filter(entity.Pipeline.name == pipeline_name).first()
    if not pipeline_entity:
        raise PipelineNotExistsException(f"Pipeline {pipeline_name} doesn't exist")
    return pipeline_entity

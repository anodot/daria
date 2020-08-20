from typing import List
from agent import destination, source, pipeline
from agent.db import Session

session = Session()


class PipelineNotExistsException(Exception):
    pass


def exists(pipeline_name: str) -> bool:
    res = session.query(
        session.query(pipeline.Pipeline).filter(pipeline.Pipeline.name == pipeline_name).exists()
    ).scalar()
    return res


def get_by_name(pipeline_name: str) -> pipeline.Pipeline:
    pipeline_ = session.query(pipeline.Pipeline).filter(pipeline.Pipeline.name == pipeline_name).first()
    if not pipeline_:
        raise PipelineNotExistsException(f"Pipeline {pipeline_name} doesn't exist")
    res = _construct_pipeline(pipeline_)
    return res


def get_by_source(source_name: str) -> List[pipeline.Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[pipeline.Pipeline]:
    pipelines = []
    for pipeline_entity in session.query(pipeline.Pipeline).all():
        pipelines.append(_construct_pipeline(pipeline_entity))
    return pipelines


def save(pipeline_: pipeline.Pipeline):
    session.add(pipeline_)
    session.commit()


def delete(pipeline_: pipeline.Pipeline):
    delete_by_name(pipeline_.name)


def delete_by_name(pipeline_name: str):
    pipeline_entity = session.query(pipeline.Pipeline).filter(pipeline.Pipeline.name == pipeline_name).first()
    if not pipeline_entity:
        raise PipelineNotExistsException(f"Pipeline {pipeline_name} doesn't exist")
    session.delete(pipeline_entity)
    session.commit()


def _construct_pipeline(pipeline_: pipeline.Pipeline) -> pipeline.Pipeline:
    pipeline_.source = source.repository.get(pipeline_.source_id)
    pipeline_.destination = destination.repository.get()
    pipeline_.override_source = pipeline_.config.pop(pipeline_.OVERRIDE_SOURCE, {})
    return pipeline_

import os

from . import pipeline
from .pipeline import Pipeline, TimestampType
from agent import destination
from agent.repository import source_repository, pipeline_repository


def create_dir():
    if not os.path.exists(pipeline_repository.PIPELINE_DIRECTORY):
        os.mkdir(pipeline_repository.PIPELINE_DIRECTORY)


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    source = source_repository.get(source_name)
    dest = destination.HttpDestination.get()
    return pipeline.Pipeline(pipeline_id, source, {}, dest)

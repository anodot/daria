import json
import os

from .pipeline import Pipeline, PipelineException, PipelineNotExistsException
from jsonschema import validate
from .. import source
from agent.destination import HttpDestination
from agent.repository import source_repository
from typing import List


def create_dir():
    if not os.path.exists(Pipeline.DIR):
        os.mkdir(Pipeline.DIR)


def load_object(pipeline_id: str) -> Pipeline:
    if not Pipeline.exists(pipeline_id):
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    with open(Pipeline.get_file_path(pipeline_id), 'r') as f:
        config = json.load(f)

    validate(config, {
        'type': 'object',
        'properties': {
            'source': {'type': 'object'},
            'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
        },
        'required': ['source', 'pipeline_id']
    })

    source_obj = source_repository.get(config['source']['name'])
    destination = HttpDestination.get()
    return Pipeline(pipeline_id, source_obj, config, destination)


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    source_obj = source_repository.get(source_name)
    destination = HttpDestination.get()
    return Pipeline(pipeline_id, source_obj, {}, destination)


def get_pipelines(source_name: str = None) -> List[Pipeline]:
    pipelines = []
    if not os.path.exists(Pipeline.DIR):
        return pipelines

    for file in os.listdir(Pipeline.DIR):
        try:
            obj = load_object(file.replace('.json', ''))
        except source.SourceConfigDeprecated as e:
            print(f'Error getting pipeline {file}. {str(e)}')
            continue
        if source_name and obj.source.name != source_name:
            continue
        pipelines.append(obj)
    return pipelines

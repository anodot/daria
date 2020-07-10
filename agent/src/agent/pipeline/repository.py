import json
import os

from jsonschema import validate
from agent import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination
from typing import List
from agent.pipeline import pipeline

PIPELINE_DIRECTORY = os.path.join(DATA_DIR, 'pipelines')


class PipelineNotExistsException(Exception):
    pass


def _get_file_path(pipeline_id: str) -> str:
    return os.path.join(PIPELINE_DIRECTORY, pipeline_id + '.json')


def exists(pipeline_id: str) -> bool:
    return os.path.isfile(_get_file_path(pipeline_id))


def get(pipeline_id: str) -> pipeline.Pipeline:
    if not exists(pipeline_id):
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    with open(_get_file_path(pipeline_id)) as f:
        config = json.load(f)

    validate(config, {
        'type': 'object',
        'properties': {
            'source': {'type': 'object'},
            'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
        },
        'required': ['source', 'pipeline_id']
    })

    source_obj = source.repository.get(config['source']['name'])
    destination = HttpDestination.get()
    return pipeline.Pipeline(pipeline_id, source_obj, config, destination)


def get_by_source(source_name: str) -> List[pipeline.Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[pipeline.Pipeline]:
    pipelines = []
    if not os.path.exists(PIPELINE_DIRECTORY):
        return pipelines
    for file in os.listdir(PIPELINE_DIRECTORY):
        try:
            obj = get(file.replace('.json', ''))
        except source.SourceConfigDeprecated as e:
            print(f'Error getting pipeline {file}. {str(e)}')
            continue
        pipelines.append(obj)
    return pipelines


def save(pipeline_obj: pipeline.Pipeline):
    with open(_get_file_path(pipeline_obj.id), 'w') as f:
        json.dump(pipeline_obj.to_dict(), f)


def delete(pipeline_obj: pipeline.Pipeline):
    delete_by_id(pipeline_obj.id)


def delete_by_id(pipeline_id: str):
    if not exists(pipeline_id):
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    os.remove(_get_file_path(pipeline_id))


def create_dir():
    if not os.path.exists(PIPELINE_DIRECTORY):
        os.mkdir(PIPELINE_DIRECTORY)

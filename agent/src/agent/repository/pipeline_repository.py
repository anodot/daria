from __future__ import annotations

import json
import os

from jsonschema import validate
from agent.cli import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination
from agent.repository import source_repository
from typing import List
from agent.pipeline import pipeline
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agent.pipeline import Pipeline

PIPELINE_DIRECTORY = os.path.join(DATA_DIR, 'pipelines')


class PipelineNotExistsException(Exception):
    pass


def __get_file_path(pipeline_id: str) -> str:
    return os.path.join(PIPELINE_DIRECTORY, pipeline_id + '.json')


def exists(pipeline_id: str) -> bool:
    return os.path.isfile(__get_file_path(pipeline_id))


def get(pipeline_id: str) -> Pipeline:
    if not exists(pipeline_id):
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    with open(__get_file_path(pipeline_id)) as f:
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
    return pipeline.Pipeline(pipeline_id, source_obj, config, destination)


def get_by_source(source_name: str) -> List[Pipeline]:
    return list(filter(lambda x: x.source.name == source_name, get_all()))


def get_all() -> List[Pipeline]:
    pipelines = []
    if not os.path.exists(PIPELINE_DIRECTORY):
        return pipelines
    for file in os.listdir(PIPELINE_DIRECTORY):
        try:
            obj = get(file.replace('.json', ''))
        except source.source.SourceConfigDeprecated as e:
            print(f'Error getting pipeline {file}. {str(e)}')
            continue
        pipelines.append(obj)
    return pipelines


def save(pipeline_obj: Pipeline):
    with open(__get_file_path(pipeline_obj.id), 'w') as f:
        json.dump(pipeline_obj.to_dict(), f)


def delete(pipeline_obj: Pipeline):
    delete_by_id(pipeline_obj.id)


def delete_by_id(pipeline_id: str):
    if not exists(pipeline_id):
        raise PipelineNotExistsException(f"Pipeline {pipeline_id} doesn't exist")
    os.remove(__get_file_path(pipeline_id))

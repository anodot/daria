import json
import os

from jsonschema import validate

from agent.cli import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination
from agent.repository import source_repository
from typing import TYPE_CHECKING, List

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
    with open(Pipeline.get_file_path(pipeline_id)) as f:
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


def get_by_source(source_name: str = None) -> List[Pipeline]:
    pipelines = []
    if not os.path.exists(Pipeline.DIR):
        return pipelines

    for file in os.listdir(Pipeline.DIR):
        try:
            obj = get(file.replace('.json', ''))
        except source.source.SourceConfigDeprecated as e:
            print(f'Error getting pipeline {file}. {str(e)}')
            continue
        if source_name and obj.source.name != source_name:
            continue
        pipelines.append(obj)
    return pipelines

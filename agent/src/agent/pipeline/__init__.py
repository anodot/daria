import json
import os

# from . import prompt, config_handlers, load_client_data
from .pipeline import Pipeline, PipelineException, PipelineNotExists
from .pipeline_manager import PipelineManager
from .. import source
from agent.destination import HttpDestination


def create_dir():
    if not os.path.exists(Pipeline.DIR):
        os.mkdir(Pipeline.DIR)


def load_object(pipeline_id: str) -> Pipeline:
    if not Pipeline.exists(pipeline_id):
        raise PipelineNotExists(f"Pipeline {pipeline_id} doesn't exist")
    with open(Pipeline.get_file_path(pipeline_id), 'r') as f:
        config = json.load(f)
    source_obj = source.load_object(config['source']['name'])
    destination = HttpDestination()
    destination.load()
    return Pipeline(pipeline_id, source_obj, config, destination)


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    source_obj = source.load_object(source_name)
    destination = HttpDestination()
    destination.load()
    return Pipeline(pipeline_id, source_obj, {}, destination)


def get_pipelines(source_name: str = None) -> list:
    pipelines = []
    for file in os.listdir(Pipeline.DIR):
        obj = load_object(file.replace('.json', ''))
        if source_name and obj.source.name != source_name:
            continue
        pipelines.append(obj)
    return pipelines

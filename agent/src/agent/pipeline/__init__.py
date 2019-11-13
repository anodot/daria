import json
import os

from . import prompt, config_handlers, load_client_data
from .pipeline import Pipeline, PipelineException, PipelineNotExists
from .. import source
from agent.destination import HttpDestination

prompters = {
    source.TYPE_MONITORING: prompt.PromptConfig,
    source.TYPE_INFLUX: prompt.PromptConfigInflux,
    source.TYPE_KAFKA: prompt.PromptConfigKafka,
    source.TYPE_MONGO: prompt.PromptConfigMongo,
    source.TYPE_MYSQL: prompt.PromptConfigJDBC,
    source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
}

loaders = {
    source.TYPE_MONITORING: load_client_data.LoadClientData,
    source.TYPE_INFLUX: load_client_data.InfluxLoadClientData,
    source.TYPE_MONGO: load_client_data.MongoLoadClientData,
    source.TYPE_KAFKA: load_client_data.KafkaLoadClientData,
    source.TYPE_MYSQL: load_client_data.JDBCLoadClientData,
    source.TYPE_POSTGRES: load_client_data.JDBCLoadClientData,
}

handlers = {
    source.TYPE_MONITORING: config_handlers.MonitoringConfigHandler,
    source.TYPE_INFLUX: config_handlers.InfluxConfigHandler,
    source.TYPE_MONGO: config_handlers.MongoConfigHandler,
    source.TYPE_KAFKA: config_handlers.KafkaConfigHandler,
    source.TYPE_MYSQL: config_handlers.JDBCConfigHandler,
    source.TYPE_POSTGRES: config_handlers.JDBCConfigHandler
}


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
    return Pipeline(pipeline_id, source_obj, config, destination, handlers[source_obj.type](),
                    prompters[source_obj.type](),
                    loaders[source_obj.type]())


def create_object(pipeline_id: str, source_name: str) -> Pipeline:
    source_obj = source.load_object(source_name)
    destination = HttpDestination()
    destination.load()
    return Pipeline(pipeline_id, source_obj, {}, destination, handlers[source_obj.type](),
                    prompters[source_obj.type](),
                    loaders[source_obj.type]())

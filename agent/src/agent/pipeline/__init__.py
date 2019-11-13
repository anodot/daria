from . import prompt, config_handlers, load_client_data
from .pipeline import Pipeline, PipelineException
from .. import source

prompters = {
        source.TYPE_INFLUX: prompt.PromptConfigInflux,
        source.TYPE_KAFKA: prompt.PromptConfigKafka,
        source.TYPE_MONGO: prompt.PromptConfigMongo,
        source.TYPE_MYSQL: prompt.PromptConfigJDBC,
        source.TYPE_POSTGRES: prompt.PromptConfigJDBC,
    }

loaders = {
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


def load_pipeline_object(pipeline_id: str) -> Pipeline:
    pass


def create_pipeline_object(pipeline_id: str, source_name: str) -> Pipeline:
    pass

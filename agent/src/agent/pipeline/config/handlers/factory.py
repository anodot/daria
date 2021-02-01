from agent import source, pipeline
from agent.pipeline import Pipeline
from agent.pipeline.config.handlers.base import BaseConfigHandler


_handlers_protocol20 = {
    source.TYPE_INFLUX: pipeline.config.handlers.influx.InfluxConfigHandler,
    source.TYPE_MONGO: pipeline.config.handlers.mongo.MongoConfigHandler,
    source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaConfigHandler,
    source.TYPE_ELASTIC: pipeline.config.handlers.elastic.ElasticConfigHandler,
    source.TYPE_SPLUNK: pipeline.config.handlers.tcp.TCPConfigHandler,
    source.TYPE_SAGE: pipeline.config.handlers.sage.SageConfigHandler,
    source.TYPE_VICTORIA: pipeline.config.handlers.victoria.VictoriaConfigHandler,
    source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCConfigHandler,
    source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCConfigHandler
}


_handlers_protocol30 = {
    source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaSchemaConfigHandler,
    source.TYPE_DIRECTORY: pipeline.config.handlers.directory.DirectoryConfigHandler,
    source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
    source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler
}


def get_config_handler(pipeline_: Pipeline) -> BaseConfigHandler:
    base_config = _get_config_loader(pipeline_).load_base_config(pipeline_)
    if pipeline_.uses_protocol_3():
        return _handlers_protocol30[pipeline_.source.type](pipeline_, base_config)

    return _handlers_protocol20[pipeline_.source.type](pipeline_, base_config)


def _get_config_loader(pipeline_: Pipeline):
    if isinstance(pipeline_, pipeline.TestPipeline):
        return pipeline.config.handlers.base.TestPipelineBaseConfigLoader
    if pipeline_.uses_protocol_3():
        return pipeline.config.handlers.base.SchemaBaseConfigLoader
    return pipeline.config.handlers.base.BaseConfigLoader

from agent import source, pipeline
from agent.pipeline import Pipeline
from agent.pipeline.config.handlers.base import BaseConfigHandler


def get_config_handler(pipeline_: Pipeline) -> BaseConfigHandler:
    base_config = _get_config_loader(pipeline_).load_base_config(pipeline_)
    if pipeline_.source.type in [source.TYPE_POSTGRES, source.TYPE_MYSQL]:
        if pipeline_.uses_protocol_3():
            return pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler(pipeline_, base_config)
        return pipeline.config.handlers.jdbc.JDBCConfigHandler(pipeline_, base_config)

    handlers = {
        source.TYPE_INFLUX: pipeline.config.handlers.influx.InfluxConfigHandler,
        source.TYPE_MONGO: pipeline.config.handlers.mongo.MongoConfigHandler,
        source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaConfigHandler,
        source.TYPE_ELASTIC: pipeline.config.handlers.elastic.ElasticConfigHandler,
        source.TYPE_SPLUNK: pipeline.config.handlers.tcp.TCPConfigHandler,
        source.TYPE_DIRECTORY: pipeline.config.handlers.directory.DirectoryConfigHandler,
        source.TYPE_SAGE: pipeline.config.handlers.sage.SageConfigHandler,
        source.TYPE_VICTORIA: pipeline.config.handlers.victoria.VictoriaConfigHandler,
        source.TYPE_ZABBIX: pipeline.config.handlers.zabbix.ZabbixConfigHandler,
    }
    return handlers[pipeline_.source.type](pipeline_, base_config)


def _get_config_loader(pipeline_: Pipeline):
    if isinstance(pipeline_, pipeline.TestPipeline):
        return pipeline.config.handlers.base.TestPipelineBaseConfigLoader
    if pipeline_.uses_protocol_3():
        return pipeline.config.handlers.base.SchemaBaseConfigLoader
    return pipeline.config.handlers.base.BaseConfigLoader

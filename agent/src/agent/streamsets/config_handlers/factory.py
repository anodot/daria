from agent import source, pipeline
from agent.pipeline import Pipeline
from agent.streamsets.config_handlers.base import BaseConfigHandler
from agent.streamsets import config_handlers


def get_config_handler(pipeline_: Pipeline) -> BaseConfigHandler:
    base_config = _get_config_loader(pipeline_).load_base_config(pipeline_)
    if pipeline_.source.type in [source.TYPE_POSTGRES, source.TYPE_MYSQL]:
        if pipeline_.uses_protocol_3():
            return config_handlers.jdbc.JDBCSchemaConfigHandler(pipeline_, base_config)
        return config_handlers.jdbc.JDBCConfigHandler(pipeline_, base_config)

    handlers = {
        source.TYPE_INFLUX: config_handlers.influx.InfluxConfigHandler,
        source.TYPE_MONGO: config_handlers.mongo.MongoConfigHandler,
        source.TYPE_KAFKA: config_handlers.kafka.KafkaConfigHandler,
        source.TYPE_ELASTIC: config_handlers.elastic.ElasticConfigHandler,
        source.TYPE_SPLUNK: config_handlers.tcp.TCPConfigHandler,
        source.TYPE_DIRECTORY: config_handlers.directory.DirectoryConfigHandler,
        source.TYPE_SAGE: config_handlers.sage.SageConfigHandler,
        source.TYPE_VICTORIA: config_handlers.victoria.VictoriaConfigHandler,
        source.TYPE_ZABBIX: config_handlers.zabbix.ZabbixConfigHandler,
    }
    return handlers[pipeline_.source.type](pipeline_, base_config)


def _get_config_loader(pipeline_: Pipeline):
    if isinstance(pipeline_, pipeline.TestPipeline):
        return config_handlers.base.TestPipelineBaseConfigLoader
    if pipeline_.uses_protocol_3():
        return config_handlers.base.SchemaBaseConfigLoader
    return config_handlers.base.BaseConfigLoader

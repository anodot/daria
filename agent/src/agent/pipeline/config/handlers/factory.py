from agent import source, pipeline
from agent.pipeline import Pipeline
from agent.pipeline.config.handlers.base import BaseConfigHandler, SchemaConfigHandler, NoSchemaConfigHandler


def get_config_handler(pipeline_: Pipeline) -> BaseConfigHandler:
    base_config = _get_config_loader(pipeline_).load_base_config(pipeline_)
    if isinstance(pipeline_, pipeline.RawPipeline):
        return _get_raw_handler(pipeline_, base_config)
    if pipeline_.uses_schema:
        return _get_schema_handler(pipeline_, base_config)
    return _get_no_schema_handler(pipeline_, base_config)


def _get_no_schema_handler(pipeline_: Pipeline, base_config: dict) -> NoSchemaConfigHandler:
    handlers_protocol20 = {
        source.TYPE_CACTI: pipeline.config.handlers.cacti.CactiConfigHandler,
        source.TYPE_CLICKHOUSE: pipeline.config.handlers.jdbc.JDBCConfigHandler,
        source.TYPE_ELASTIC: pipeline.config.handlers.elastic.ElasticConfigHandler,
        source.TYPE_INFLUX: pipeline.config.handlers.influx.InfluxConfigHandler,
        source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaConfigHandler,
        source.TYPE_MONGO: pipeline.config.handlers.mongo.MongoConfigHandler,
        source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCConfigHandler,
        source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCConfigHandler,
        source.TYPE_PROMETHEUS: pipeline.config.handlers.promql.PromQLConfigHandler,
        source.TYPE_SAGE: pipeline.config.handlers.sage.SageConfigHandler,
        source.TYPE_SOLARWINDS: pipeline.config.handlers.solarwinds.SolarWindsConfigHandler,
        source.TYPE_SPLUNK: pipeline.config.handlers.tcp.TCPConfigHandler,
        source.TYPE_THANOS: pipeline.config.handlers.promql.PromQLConfigHandler,
        source.TYPE_VICTORIA: pipeline.config.handlers.promql.PromQLConfigHandler,
        source.TYPE_ZABBIX: pipeline.config.handlers.zabbix.ZabbixConfigHandler,
    }
    return handlers_protocol20[pipeline_.source.type](pipeline_, base_config)


def _get_raw_handler(pipeline_: Pipeline, base_config: dict) -> BaseConfigHandler:
    handlers = {
        source.TYPE_CLICKHOUSE: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
        source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
        source.TYPE_ORACLE: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
        source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
        source.TYPE_SNMP: pipeline.config.handlers.snmp.SNMPRawConfigHandler,
    }
    return handlers[pipeline_.source.type](pipeline_, base_config)


def _get_schema_handler(pipeline_: Pipeline, base_config: dict) -> SchemaConfigHandler:
    handlers_protocol30 = {
        source.TYPE_CLICKHOUSE: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_DIRECTORY: pipeline.config.handlers.directory.DirectoryConfigHandler,
        source.TYPE_INFLUX: pipeline.config.handlers.influx.InfluxSchemaConfigHandler,
        source.TYPE_INFLUX_2: pipeline.config.handlers.influx.Influx2SchemaConfigHandler,
        source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaSchemaConfigHandler,
        source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_OBSERVIUM: pipeline.config.handlers.observium.ObserviumConfigHandler,
        source.TYPE_ORACLE: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_SNMP: pipeline.config.handlers.snmp.SNMPConfigHandler,
    }
    return handlers_protocol30[pipeline_.source.type](pipeline_, base_config)


def _get_config_loader(pipeline_: Pipeline):
    if isinstance(pipeline_, pipeline.TestPipeline):
        return pipeline.config.handlers.base.TestPipelineBaseConfigLoader
    if isinstance(pipeline_, pipeline.RawPipeline):
        return pipeline.config.handlers.base.RawConfigLoader
    if pipeline_.uses_schema:
        return pipeline.config.handlers.base.SchemaBaseConfigLoader
    return pipeline.config.handlers.base.NoSchemaConfigLoader

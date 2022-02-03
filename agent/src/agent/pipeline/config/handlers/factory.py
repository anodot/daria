from agent import source, pipeline
from agent.pipeline import Pipeline
from agent.pipeline.config.handlers.base import ConfigHandler, SchemaConfigHandler, NoSchemaConfigHandler


def get_config_handler(pipeline_: Pipeline) -> ConfigHandler:
    base_config = _get_config_loader(pipeline_).load_base_config(pipeline_)
    if isinstance(pipeline_, pipeline.RawPipeline):
        return _get_raw_handler(pipeline_, base_config)
    if isinstance(pipeline_, pipeline.TestPipeline):
        return _get_test_handler(pipeline_, base_config)
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
        source.TYPE_TOPOLOGY: pipeline.config.handlers.topology.TopologyConfigHandler,
        source.TYPE_VICTORIA: pipeline.config.handlers.promql.PromQLConfigHandler,
        source.TYPE_ZABBIX: pipeline.config.handlers.zabbix.ZabbixConfigHandler,
    }
    return handlers_protocol20[pipeline_.source.type](pipeline_, base_config)


def _get_raw_handler(pipeline_: Pipeline, base_config: dict) -> ConfigHandler:
    handlers = {
        source.TYPE_CLICKHOUSE: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
        source.TYPE_DATABRICKS: pipeline.config.handlers.jdbc.JDBCRawConfigHandler,
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
        source.TYPE_DATABRICKS: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_INFLUX: pipeline.config.handlers.influx.InfluxSchemaConfigHandler,
        source.TYPE_INFLUX_2: pipeline.config.handlers.influx.Influx2SchemaConfigHandler,
        source.TYPE_KAFKA: pipeline.config.handlers.kafka.KafkaSchemaConfigHandler,
        source.TYPE_MYSQL: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_OBSERVIUM: pipeline.config.handlers.observium.ObserviumConfigHandler,
        source.TYPE_ORACLE: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.JDBCSchemaConfigHandler,
        source.TYPE_PROMETHEUS: pipeline.config.handlers.promql.PromQLSchemaConfigHandler,
        source.TYPE_SAGE: pipeline.config.handlers.sage.SageSchemaConfigHandler,
        source.TYPE_SNMP: pipeline.config.handlers.snmp.SNMPConfigHandler,
        source.TYPE_THANOS: pipeline.config.handlers.promql.PromQLSchemaConfigHandler,
        source.TYPE_VICTORIA: pipeline.config.handlers.promql.PromQLSchemaConfigHandler,
    }
    return handlers_protocol30[pipeline_.source.type](pipeline_, base_config)


def _get_test_handler(pipeline_: Pipeline, base_config: dict) -> ConfigHandler:
    handlers = {
        source.TYPE_CACTI: pipeline.config.handlers.cacti.CactiConfigHandler,
        source.TYPE_CLICKHOUSE: pipeline.config.handlers.jdbc.TestJDBCConfigHandler,
        source.TYPE_DIRECTORY: pipeline.config.handlers.directory.TestDirectoryConfigHandler,
        source.TYPE_DATABRICKS: pipeline.config.handlers.jdbc.TestJDBCConfigHandler,
        source.TYPE_ELASTIC: pipeline.config.handlers.elastic.ElasticConfigHandler,
        source.TYPE_INFLUX: pipeline.config.handlers.influx.TestInfluxConfigHandler,
        source.TYPE_INFLUX_2: pipeline.config.handlers.influx.TestInflux2ConfigHandler,
        source.TYPE_KAFKA: pipeline.config.handlers.kafka.TestKafkaConfigHandler,
        source.TYPE_MONGO: pipeline.config.handlers.mongo.MongoConfigHandler,
        source.TYPE_MYSQL: pipeline.config.handlers.jdbc.TestJDBCConfigHandler,
        source.TYPE_OBSERVIUM: pipeline.config.handlers.observium.TestObserviumConfigHandler,
        source.TYPE_ORACLE: pipeline.config.handlers.jdbc.TestJDBCConfigHandler,
        source.TYPE_POSTGRES: pipeline.config.handlers.jdbc.TestJDBCConfigHandler,
        source.TYPE_PROMETHEUS: pipeline.config.handlers.promql.TestPromQLConfigHandler,
        source.TYPE_SAGE: pipeline.config.handlers.sage.SageConfigHandler,
        source.TYPE_SOLARWINDS: pipeline.config.handlers.solarwinds.SolarWindsConfigHandler,
        source.TYPE_SPLUNK: pipeline.config.handlers.tcp.TCPConfigHandler,
        source.TYPE_THANOS: pipeline.config.handlers.promql.TestPromQLConfigHandler,
        source.TYPE_VICTORIA: pipeline.config.handlers.promql.TestPromQLConfigHandler,
        source.TYPE_ZABBIX: pipeline.config.handlers.zabbix.TestZabbixConfigHandler,
    }
    return handlers[pipeline_.source.type](pipeline_, base_config)


def _get_config_loader(pipeline_: Pipeline):
    if isinstance(pipeline_, pipeline.TestPipeline):
        return pipeline.config.loader.TestPipelineConfigLoader
    if isinstance(pipeline_, pipeline.RawPipeline):
        return pipeline.config.loader.RawConfigLoader
    if pipeline_.uses_schema:
        return pipeline.config.loader.SchemaConfigLoader
    return pipeline.config.loader.NoSchemaConfigLoader

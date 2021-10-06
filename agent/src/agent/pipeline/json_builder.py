import json
import os
import traceback
import jsonschema

from typing import List, Callable
from agent import source, pipeline
from agent.data_extractor.snmp import snmp
from agent.modules.logger import get_logger
from agent.pipeline import Pipeline
from agent.pipeline.config import expression_parser

logger_ = get_logger(__name__, stdout=True)


def build_using_file(file):
    build_multiple(extract_configs(file))


def edit_using_file(file):
    edit_multiple(extract_configs(file))


def build_multiple(configs: list) -> List[Pipeline]:
    return _build_multiple(configs, build)


def build_multiple_raw(configs: list) -> List[Pipeline]:
    return _build_multiple(configs, build_raw)


def _build_multiple(configs: list, build_func: Callable) -> List[Pipeline]:
    _validate_configs_for_create(configs)
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            pipeline.manager.check_pipeline_id(config['pipeline_id'])
            pipelines.append(build_func(config))
        except Exception as e:
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {traceback.format_exc()}'
    if exceptions:
        raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def build(config: dict) -> Pipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.manager.create_object(config['pipeline_id'], config['source'])
    return _build(config, pipeline_)


def build_raw(config: dict) -> Pipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.RawPipeline(
        config['pipeline_id'],
        source.repository.get_by_name(config['source'])
    )
    return _build(config, pipeline_)


def _build(config: dict, pipeline_: Pipeline) -> Pipeline:
    _load_config(pipeline_, config)
    pipeline.manager.create(pipeline_)
    logger_.info(f'Pipeline {pipeline_.name} created')
    return pipeline_


def edit_multiple(configs: list) -> List[Pipeline]:
    if not isinstance(configs, list):
        raise ValueError(f'Provided data must be a list of configs, {type(configs).__name__} provided instead')
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            pipelines.append(edit(config))
        except Exception as e:
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {e}'
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def edit(config: dict) -> Pipeline:
    pipeline_ = pipeline.repository.get_by_id(config['pipeline_id'])

    _load_config(pipeline_, config, is_edit=True)

    pipeline.manager.update(pipeline_)
    return pipeline_


def extract_configs(file) -> list:
    data = json.load(file)
    file.seek(0)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['pipeline_id']
        }
    }
    jsonschema.validate(data, json_schema)
    return data


def _validate_configs_for_create(configs: list):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'type': 'string', 'enum': source.repository.get_all_names()},
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['source', 'pipeline_id']
        }
    }
    jsonschema.validate(configs, json_schema)


def _validate_config_for_create(config: dict):
    json_schema = {
        'type': 'object',
        'properties': {
            'source': {'type': 'string', 'enum': source.repository.get_all_names()},
            'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
        },
        'required': ['source', 'pipeline_id']
    }
    jsonschema.validate(config, json_schema)


def _load_config(pipeline_: Pipeline, config: dict, is_edit=False):
    if isinstance(pipeline_, pipeline.RawPipeline):
        config['uses_schema'] = False
    elif 'uses_schema' not in config:
        if is_edit:
            config['uses_schema'] = pipeline_.config.get('uses_schema', False)
        else:
            config['uses_schema'] = pipeline.manager.supports_schema(pipeline_)

    config = get_file_loader(pipeline_, is_edit).load(config)

    pipeline_.set_config(config)
    # todo too many validations, 4 validations here
    pipeline.config.validators.get_config_validator(pipeline_.source.type).validate(pipeline_)


class LoadClientData:
    VALIDATION_SCHEMA_FILE_NAME = ''
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions'

    def __init__(self, pipeline_: Pipeline, is_edit: bool):
        self.client_config = {}
        self.pipeline = pipeline_
        self.edit = is_edit

    def load(self, client_config) -> dict:
        self.client_config = client_config
        if 'override_source' not in self.client_config:
            self.client_config['override_source'] = {}

        self._validate_json_schema()

        client_config.pop('source', None)

        self._load_filtering()
        self._load_transformations()

        return self.client_config

    @property
    def definitions_dir(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), self.VALIDATION_SCHEMA_DIR_NAME)

    def _validate_json_schema(self):
        with open(os.path.join(self.definitions_dir, self.VALIDATION_SCHEMA_FILE_NAME + '.json')) as f:
            schema = json.load(f)
        if self.edit:
            schema['required'] = []

        jsonschema.validate(self.client_config, schema)

    def _load_filtering(self):
        condition = self.client_config.get('filter', {}).get('condition')
        if condition:
            expression_parser.condition.validate(condition)

    def _load_transformations(self):
        transformation_file = self.client_config.get('transform', {}).get('file')
        if not transformation_file:
            return

        expression_parser.transformation.validate_file(transformation_file)
        with open(transformation_file) as f:
            self.client_config['transform']['config'] = f.read()

    def _load_dimensions(self):
        if type(self.client_config.get('dimensions')) == list:
            self.client_config['dimensions'] = {'required': [], 'optional': self.client_config['dimensions']}


class CactiLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'cacti'

    def load(self, client_config: dict):
        super().load(client_config)
        if 'timestamp' not in self.client_config:
            self.client_config['timestamp'] = {'type': 'unix'}
        if 'add_graph_name_dimension' not in self.client_config and not self.edit:
            self.client_config['add_graph_name_dimension'] = False
        if 'convert_bytes_into_bits' not in self.client_config and not self.edit:
            self.client_config['convert_bytes_into_bits'] = False
        return self.client_config


class MongoLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'mongo'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        return self.client_config


class KafkaLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'kafka'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        if 'timestamp' not in self.client_config and not self.edit:
            self.client_config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        if source.KafkaSource.CONFIG_CONSUMER_GROUP not in self.client_config['override_source']:
            self.client_config['override_source'][source.KafkaSource.CONFIG_CONSUMER_GROUP] = \
                "agent_" + self.client_config['pipeline_id']
        return self.client_config


class InfluxLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'influx'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        self._set_timestamp()
        return self.client_config

    def _set_timestamp(self):
        self.client_config['timestamp'] = {
            'type': 'unix_ms',
            'name': 'time',
        }


class Influx2LoadClientData(InfluxLoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'influx2'

    def load(self, client_config):
        super().load(client_config)
        self.client_config['uses_schema'] = True
        return self.client_config

    def _set_timestamp(self):
        self.client_config['timestamp'] = {
            'type': 'unix',
            'name': '_time',
        }


class JDBCLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'


class JDBCRawLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'


class ElasticLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'elastic'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        if 'query_file' in self.client_config:
            with open(self.client_config['query_file']) as f:
                self.client_config['override_source'][source.ElasticSource.CONFIG_QUERY] = f.read()

        return self.client_config


class ObserviumLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'observium'

    def load(self, client_config):
        super().load(client_config)
        self.client_config['timestamp'] = {'type': 'unix'}
        self.client_config['uses_schema'] = True
        return self.client_config


class TcpLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'tcp_server'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        return self.client_config


class DirectoryLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'directory'

    def load(self, client_config):
        super().load(client_config)
        self._load_dimensions()
        return self.client_config


class SageLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'sage'

    def load(self, client_config):
        super().load(client_config)
        if 'query_file' in self.client_config:
            with open(self.client_config['query_file']) as f:
                self.client_config['query'] = f.read()
        return self.client_config


class SNMPLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'

    def load(self, client_config):
        super().load(client_config)
        self.client_config['timestamp'] = {}
        self.client_config['timestamp']['type'] = 'unix'
        self.client_config['uses_schema'] = True
        self._add_default_dimensions()
        return self.client_config

    def _add_default_dimensions(self):
        if 'dimensions' not in self.client_config:
            self.client_config['dimensions'] = []
        self.client_config['oids'].append(snmp.HOSTNAME_OID)
        self.client_config['dimensions'].append(snmp.HOSTNAME_OID)


class SNMPRawLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def load(self, client_config):
        super().load(client_config)
        self.client_config['timestamp'] = {}
        self.client_config['timestamp']['type'] = 'unix'
        return self.client_config


class SolarWindsClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'solarwinds'


class PromQLLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'promql'


class ZabbixLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'zabbix'

    def load(self, client_config):
        super().load(client_config)
        self.client_config['timestamp'] = {}
        self.client_config['timestamp']['type'] = 'unix'
        self.client_config['timestamp']['name'] = 'clock'
        if 'query' in self.pipeline.config and self.pipeline.config['query'] != self.client_config['query']:
            self.client_config['query_changed'] = True
        return self.client_config


def get_file_loader(pipeline_: Pipeline, is_edit=False) -> LoadClientData:
    if isinstance(pipeline_, pipeline.RawPipeline):
        return _get_raw_loader(pipeline_, is_edit)
    return _get_loader(pipeline_, is_edit)


def _get_loader(pipeline_: Pipeline, is_edit: bool) -> LoadClientData:
    loaders = {
        source.TYPE_CACTI: CactiLoadClientData,
        source.TYPE_CLICKHOUSE: JDBCLoadClientData,
        source.TYPE_DIRECTORY: DirectoryLoadClientData,
        source.TYPE_ELASTIC: ElasticLoadClientData,
        source.TYPE_INFLUX: InfluxLoadClientData,
        source.TYPE_INFLUX_2: Influx2LoadClientData,
        source.TYPE_KAFKA: KafkaLoadClientData,
        source.TYPE_MONGO: MongoLoadClientData,
        source.TYPE_MYSQL: JDBCLoadClientData,
        source.TYPE_ORACLE: JDBCLoadClientData,
        source.TYPE_POSTGRES: JDBCLoadClientData,
        source.TYPE_OBSERVIUM: ObserviumLoadClientData,
        source.TYPE_SAGE: SageLoadClientData,
        source.TYPE_SNMP: SNMPLoadClientData,
        source.TYPE_SOLARWINDS: SolarWindsClientData,
        source.TYPE_SPLUNK: TcpLoadClientData,
        source.TYPE_THANOS: PromQLLoadClientData,
        source.TYPE_VICTORIA: PromQLLoadClientData,
        source.TYPE_ZABBIX: ZabbixLoadClientData,
    }
    return loaders[pipeline_.source.type](pipeline_, is_edit)


def _get_raw_loader(pipeline_: Pipeline, is_edit: bool) -> LoadClientData:
    # todo do all they support?
    loaders = {
        source.TYPE_CLICKHOUSE: JDBCRawLoadClientData,
        source.TYPE_MYSQL: JDBCRawLoadClientData,
        source.TYPE_POSTGRES: JDBCRawLoadClientData,
        source.TYPE_SNMP: SNMPRawLoadClientData,
    }
    return loaders[pipeline_.source.type](pipeline_, is_edit)

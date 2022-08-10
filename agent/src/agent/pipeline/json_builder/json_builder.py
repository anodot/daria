import json
import os
import jsonschema

from abc import ABC, abstractmethod
from typing import List, Callable
from agent import source, pipeline
from agent.modules import validator, expression_parser
from agent.modules.logger import get_logger
from agent.modules.tools import deep_update
from agent.pipeline import Pipeline, TopologyPipeline

logger_ = get_logger(__name__, stdout=True)


def build_using_file(file) -> List[Pipeline]:
    return build_multiple(extract_configs(file))


def edit_using_file(file) -> List[Pipeline]:
    return edit_multiple(extract_configs(file))


def build_multiple(configs: list) -> List[Pipeline]:
    return _build_multiple(configs, build)


def build_raw_using_file(file) -> List[Pipeline]:
    return _build_multiple(extract_configs(file), build_raw)


def build_events_using_file(file) -> List[Pipeline]:
    return _build_multiple(extract_configs(file), build_events)


def build_topology_using_file(file) -> List[Pipeline]:
    return _build_multiple(extract_configs(file), build_topology)


def _build_multiple(configs: list, build_func: Callable) -> List[Pipeline]:
    _validate_configs_for_create(configs)
    exceptions = {}
    pipelines = []
    for config in configs:
        try:
            pipeline.manager.check_pipeline_id(config['pipeline_id'])
            pipelines.append(build_func(config))
        except Exception as e:
            exceptions[config['pipeline_id']] = f'{type(e).__name__}: {e}'
            logger_.debug(e, exc_info=True)
    if exceptions:
        raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def build(config: dict) -> Pipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.manager.create_pipeline(config['pipeline_id'], config['source'])
    return _build(config, pipeline_)


def build_raw(config: dict) -> Pipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.manager.create_raw_pipeline(config['pipeline_id'], config['source'])
    return _build(config, pipeline_)


def build_events(config: dict) -> Pipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.manager.create_events_pipeline(config['pipeline_id'], config['source'])
    return _build(config, pipeline_)


def build_topology(config: dict) -> TopologyPipeline:
    _validate_config_for_create(config)
    pipeline_ = pipeline.manager.create_topology_pipeline(config['pipeline_id'], config['source'])
    return _build(config, pipeline_)


def _build(config: dict, pipeline_: Pipeline) -> Pipeline:
    pipeline.manager.create(pipeline_, config)
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
            logger_.debug(e, exc_info=True)
        if exceptions:
            raise pipeline.PipelineException(json.dumps(exceptions))
    return pipelines


def edit(config: dict) -> Pipeline:
    pipeline_ = pipeline.repository.get_by_id(config['pipeline_id'])
    pipeline.manager.update(pipeline_, config)
    return pipeline_


def extract_configs(file) -> list:
    data = json.load(file)
    file.seek(0)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'pipeline_id': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 100
                }
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
                'source': {
                    'type': 'string',
                    'enum': source.repository.get_all_names()
                },
                'pipeline_id': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 100
                },
                'units': {
                    'type': 'object',
                },
                'notifications': {
                    'type': 'object',
                    'properties': {
                        'no_data':
                            {'type': 'string', 'pattern': r'(?![0])\d{1,}[hm]'}
                    },
                },
            },
            'required': ['source', 'pipeline_id']
        }
    }
    jsonschema.validate(configs, json_schema)


def _validate_config_for_create(config: dict):
    json_schema = {
        'type': 'object',
        'properties': {
            'source': {
                'type': 'string',
                'enum': source.repository.get_all_names()
            },
            'pipeline_id': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 100
            },
            'units': {
                'type': 'object',
            },
            'notifications': {
                'type': 'object',
                'properties': {
                    'no_data':
                        {'type': 'string', 'pattern': r'(?![0])\d{1,}[hm]'}
                },
            },
            'pipeline_type': {'type': 'string', 'enum': pipeline.PIPELINE_TYPES},
        },
        'required': ['source', 'pipeline_id']
    }
    jsonschema.validate(config, json_schema)


class _SchemaChooser:
    @staticmethod
    def choose(pipeline_: Pipeline, config: dict, is_edit=False) -> bool:
        if not pipeline.manager.supports_schema(pipeline_):
            return False
        elif 'uses_schema' not in config:
            # we would return False earlier if it doesn't support schema so if it's not edit it means it should use it
            return bool(pipeline_.config.get('uses_schema', False)) if is_edit else True
        else:
            return bool(config['uses_schema'])


class _PromQLSchemaChooser(_SchemaChooser):
    @staticmethod
    def choose(pipeline_: Pipeline, config: dict, is_edit=False) -> bool:
        conf_uses = False if 'uses_schema' not in config else bool(config['uses_schema'])
        # PromQL pipelines support schema only if dimensions and values are specified
        actual_schema = (
                _SchemaChooser.choose(pipeline_, config, is_edit)
                and 'dimensions' in config
                and bool(config['dimensions'])
                and 'values' in config
                and bool(config['values'])
        )
        if conf_uses and not actual_schema:
            raise ConfigurationException(
                'PromQL pipelines support protocol 3.0 only if `dimensions` and `values` are specified'
            )
        return actual_schema


def get_schema_chooser(pipeline_: Pipeline) -> _SchemaChooser:
    if isinstance(pipeline_.source, source.PromQLSource):
        return _PromQLSchemaChooser()
    return _SchemaChooser()


class IBuilder(ABC):
    VALIDATION_SCHEMA_FILE_NAME = ''
    VALIDATION_SCHEMA_DIR_NAME = ''

    def __init__(self, pipeline_: Pipeline, config: dict, is_edit: bool):
        self.config = config
        self.pipeline = pipeline_
        self.edit = is_edit

    @abstractmethod
    def build(self) -> Pipeline:
        pass

    @property
    def definitions_dir(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), self.VALIDATION_SCHEMA_DIR_NAME)

    def _get_validation_file_path(self):
        return os.path.join(self.definitions_dir, f'{self.VALIDATION_SCHEMA_FILE_NAME}.json')


class Builder(IBuilder):
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions'

    def build(self) -> Pipeline:
        self._load_config()
        self.pipeline.set_config(self.config)
        return self.pipeline

    def _load_config(self):
        if 'override_source' not in self.config:
            self.config['override_source'] = {}
        self._validate_periodic_watermark_delay()
        self._load_dvp_config_with_default()
        self._validate_json_schema()
        self.config.pop('source', None)
        self._load_filtering()
        self._load_transformations()

    def _validate_periodic_watermark_delay(self):
        if (
                'periodic_watermark' in self.config and 'interval' in self.config
                and int(self.config['periodic_watermark'].get('delay', 0)) >= int(self.config['interval'])
        ):
            raise ConfigurationException('Periodic watermark delay must be less than interval')

    def _validate_json_schema(self):
        self._validate_dvp_config_json_schema()
        _validate_schema(self._get_validation_file_path(), self.config, self.edit)

    def _validate_dvp_config_json_schema(self):
        if 'dvpConfig' not in self.config:
            return
        _validate_schema(os.path.join(self.definitions_dir, 'dvp_config.json'), self.config['dvpConfig'], False)

    def _load_dvp_config_with_default(self):
        if 'dvpConfig' not in self.config:
            return

        src_dvp_config = self.config['dvpConfig'].copy()
        self.config['dvpConfig'] = {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 24,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }
        deep_update(src_dvp_config, self.config['dvpConfig'])

    def _load_filtering(self):
        if condition := self.config.get('filter', {}).get('condition'):
            expression_parser.condition.validate(condition)

    def _load_transformations(self):
        if transformation_file := self.config.get('transform', {}).get('file'):
            expression_parser.transformation.validate_file(transformation_file)
            with open(transformation_file) as f:
                self.config['transform']['config'] = f.read()
        if transformation_script_file := self.config.get('transform_script', {}).get('file'):
            if os.path.splitext(transformation_script_file)[1] == '.py':
                validator.validate_python_file(transformation_script_file)
            with open(transformation_script_file) as f:
                self.config['transform_script']['config'] = f.read()

    def _load_dimensions(self):
        if type(self.config.get('dimensions')) == list:
            self.config['dimensions'] = {'required': [], 'optional': self.config['dimensions']}


class EventsBuilder(IBuilder):
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/events'

    def build(self) -> Pipeline:
        _validate_schema(self._get_validation_file_path(), self.config, self.edit)
        self.pipeline.set_config(self.config)
        return self.pipeline


def _validate_schema(file_path: str, config: dict, is_edit: bool):
    with open(file_path) as f:
        schema = json.load(f)
    if is_edit:
        schema['required'] = []
    jsonschema.validate(config, schema)


class ConfigurationException(Exception):
    pass

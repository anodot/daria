import json
import os
import traceback
import jsonschema

from typing import List, Callable
from agent import source, pipeline
from agent.modules import validator
from agent.modules.logger import get_logger
from agent.pipeline import Pipeline, json_builder
from agent.pipeline.config import expression_parser

logger_ = get_logger(__name__, stdout=True)


def build_using_file(file) -> List[Pipeline]:
    return build_multiple(extract_configs(file))


def edit_using_file(file) -> List[Pipeline]:
    return edit_multiple(extract_configs(file))


def build_multiple(configs: list) -> List[Pipeline]:
    return _build_multiple(configs, build)


def build_raw_using_file(file) -> List[Pipeline]:
    return _build_multiple(extract_configs(file), build_raw)


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
    pipeline_ = pipeline.RawPipeline(config['pipeline_id'], source.repository.get_by_name(config['source']))
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
                }
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
            }
        },
        'required': ['source', 'pipeline_id']
    }
    jsonschema.validate(config, json_schema)


def _load_config(pipeline_: Pipeline, config: dict, is_edit=False):
    config['uses_schema'] = _get_schema_chooser(pipeline_).choose(pipeline_, config, is_edit)
    json_builder.get(pipeline_, config, is_edit).build()
    # todo too many validations, 4 validations here
    pipeline.config.validators.get_config_validator(pipeline_.source.type).validate(pipeline_)


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
            _SchemaChooser.choose(pipeline_, config, is_edit) and 'dimensions' in config and bool(config['dimensions'])
            and 'values' in config and bool(config['values'])
        )
        if conf_uses and not actual_schema:
            raise ConfigurationException(
                'PromQL pipelines support protocol 3.0 only if `dimensions` and `values` are specified'
            )
        return actual_schema


def _get_schema_chooser(pipeline_: Pipeline) -> _SchemaChooser:
    if isinstance(pipeline_.source, source.PromQLSource):
        return _PromQLSchemaChooser()
    return _SchemaChooser()


class Builder:
    VALIDATION_SCHEMA_FILE_NAME = ''
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions'

    def __init__(self, pipeline_: Pipeline, config: dict, is_edit: bool):
        self.config = config
        self.pipeline = pipeline_
        self.edit = is_edit

    def build(self) -> Pipeline:
        self._load_config()
        self.pipeline.set_config(self.config)
        return self.pipeline

    def _load_config(self):
        if 'override_source' not in self.config:
            self.config['override_source'] = {}
        self._validate_json_schema()
        self.config.pop('source', None)
        self._load_filtering()
        self._load_transformations()

    @property
    def definitions_dir(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), self.VALIDATION_SCHEMA_DIR_NAME)

    def _validate_json_schema(self):
        if 'dvpConfig' in self.config:
            self._validate_dvp_config_json_schema()
        with open(os.path.join(self.definitions_dir, self.VALIDATION_SCHEMA_FILE_NAME + '.json')) as f:
            schema = json.load(f)
        if self.edit:
            schema['required'] = []
        jsonschema.validate(self.config, schema)

    def _validate_dvp_config_json_schema(self):
        with open(os.path.join(self.definitions_dir, 'dvp_config.json')) as f:
            schema = json.load(f)
        jsonschema.validate(self.config['dvpConfig'], schema)

    def _load_filtering(self):
        if condition := self.config.get('filter', {}).get('condition'):
            expression_parser.condition.validate(condition)

    def _load_transformations(self):
        if transformation_file := self.config.get('transform', {}).get('file'):
            expression_parser.transformation.validate_file(transformation_file)
            with open(transformation_file) as f:
                self.config['transform']['config'] = f.read()
        if transformation_script_file := self.config.get('transform_script', {}).get('file'):
            validator.validate_python_file(transformation_script_file)
            with open(transformation_script_file) as f:
                self.config['transform_script']['config'] = f.read()

    def _load_dimensions(self):
        if type(self.config.get('dimensions')) == list:
            self.config['dimensions'] = {'required': [], 'optional': self.config['dimensions']}


class ConfigurationException(Exception):
    pass

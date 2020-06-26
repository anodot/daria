import click
import json
import os

from .. import source
from agent.constants import DATA_DIR, HOSTNAME
from agent.destination.http import HttpDestination
from enum import Enum


class TimestampType(Enum):
    STRING = 'string'
    DATETIME = 'datetime'
    UNIX = 'unix'
    UNIX_MS = 'unix_ms'


class FlushBucketSize(Enum):
    MIN_1 = '1m'
    MIN_5 = '5m'
    HOUR_1 = '1h'
    DAY_1 = '1d'
    WEEK_1 = '1w'

    def total_seconds(self):
        if self == self.MIN_1:
            return 60
        if self == self.MIN_5:
            return 60 * 5
        if self == self.HOUR_1:
            return 60 * 60
        if self == self.DAY_1:
            return 60 * 60 * 24
        if self == self.WEEK_1:
            return 60 * 60 * 24 * 7


class Pipeline:
    DIR = os.path.join(DATA_DIR, 'pipelines')
    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'
    STATUS_STOPPING = 'STOPPING'
    OVERRIDE_SOURCE = 'override_source'
    FLUSH_BUCKET_SIZE = 'flush_bucket_size'

    TARGET_TYPES = ['counter', 'gauge', 'running_counter']

    def __init__(self, pipeline_id: str,
                 source_obj: source.Source,
                 config: dict,
                 destination: HttpDestination):
        self.id = pipeline_id
        self.config = config
        self.source = source_obj
        self.destination = destination
        self.old_config = None
        self.override_source = config.pop(self.OVERRIDE_SOURCE, {})

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.id)

    @property
    def constant_dimensions(self) -> dict:
        return self.config.get('properties', {})

    @property
    def flush_bucket_size(self) -> FlushBucketSize:
        return FlushBucketSize(self.config.get(self.FLUSH_BUCKET_SIZE))

    @flush_bucket_size.setter
    def flush_bucket_size(self, value: str):
        self.config[self.FLUSH_BUCKET_SIZE] = FlushBucketSize(value).value

    @property
    def constant_dimensions_names(self):
        return self.constant_dimensions.keys()

    @property
    def dimensions(self):
        dimensions = self.config['dimensions']
        if type(self.config['dimensions']) is dict:
            dimensions = self.config['dimensions']['required'] + self.config['dimensions'].get('optional', [])
        return dimensions

    @property
    def dimensions_names(self):
        return [self.replace_chars(d) for d in self.dimensions]

    @property
    def dimensions_paths(self):
        return [self.get_property_path(value) for value in self.dimensions]

    @property
    def required_dimensions_paths(self):
        return [self.get_property_path(value) for value in self.config['dimensions']['required']]

    @property
    def timestamp_path(self) -> str:
        return self.get_property_path(self.config['timestamp']['name'])

    @property
    def timestamp_type(self) -> TimestampType:
        return TimestampType(self.config['timestamp']['type'])

    @property
    def timestamp_format(self) -> str:
        return self.config['timestamp'].get('format')

    @property
    def values(self):
        return self.config['values'].keys()

    @property
    def values_paths(self):
        return [self.get_property_path(value) for value in self.values]

    @property
    def target_types(self):
        return list(self.config['values'].values())

    @property
    def measurement_names(self):
        return [self.replace_chars(self.config.get('measurement_names', {}).get(key, key)) for key in self.values]

    @property
    def measurement_names_paths(self):
        return [self.get_property_path(value) for value in self.measurement_names]

    @property
    def target_types_paths(self):
        return [self.get_property_path(t_type) for t_type in self.target_types]

    @property
    def count_records(self) -> bool:
        return self.config.get('count_records', False)

    @property
    def count_records_measurement_name(self) -> str:
        return self.replace_chars(self.config.get('count_records_measurement_name', 'count'))

    @property
    def static_what(self) -> bool:
        return self.config.get('static_what', True)

    @property
    def transformations_file_path(self) -> str:
        return self.config.get('transform', {}).get('file')

    @property
    def filter_condition(self) -> str:
        return self.config.get('filter', {}).get('condition')

    @property
    def tags(self) -> dict:
        return self.config.get('tags', {})

    @property
    def values_array_path(self) -> str:
        return self.config.get('values_array_path', '')

    @property
    def values_array_filter_metrics(self) -> list:
        return self.config.get('values_array_filter_metrics', [])

    @property
    def query_file(self) -> str:
        return self.config.get('query_file')

    @property
    def interval(self) -> str:
        return self.config.get('interval')

    @property
    def delay(self) -> str:
        return self.config.get('delay', 0)

    def get_schema(self):
        return self.config.get('schema', {})

    def get_schema_id(self):
        return self.get_schema().get('id')

    def to_dict(self):
        return {
            **self.config,
            self.OVERRIDE_SOURCE: self.override_source,
            'pipeline_id': self.id,
            'source': {'name': self.source.name},
        }

    @classmethod
    def get_file_path(cls, pipeline_id: str) -> str:
        return os.path.join(cls.DIR, pipeline_id + '.json')

    @classmethod
    def exists(cls, pipeline_id: str) -> bool:
        return os.path.isfile(cls.get_file_path(pipeline_id))

    def set_config(self, config: dict):
        self.config.update(config)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def get_property_path(self, property_value: str) -> str:
        mapping = self.source.config.get('csv_mapping', {})
        for idx, item in mapping.items():
            if item == property_value:
                return str(idx)

        return str(property_value)

    @classmethod
    def replace_chars(cls, property_name):
        return property_name.replace('/', '_').replace('.', '_').replace(' ', '_')

    def get_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.destination.host_id],
            'source_host_name': [HOSTNAME],
            'pipeline_id': [self.id],
            'pipeline_type': [self.source.type],
            **self.tags
        }


class PipelineException(click.ClickException):
    pass


class PipelineNotExistsException(PipelineException):
    pass

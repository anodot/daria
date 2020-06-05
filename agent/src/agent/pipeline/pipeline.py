import click
import json
import os

from .. import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination


class Pipeline:
    DIR = os.path.join(DATA_DIR, 'pipelines')
    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'
    STATUS_STOPPING = 'STOPPING'
    OVERRIDE_SOURCE = 'override_source'

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
    def constant_dimensions_names(self):
        return self.constant_dimensions.keys()

    @property
    def dimensions_names(self):
        dimension_names = self.config['dimensions']
        if self.config['dimensions'] is dict:
            dimension_names = self.config['dimensions']['required'] + self.config['dimensions'].get('optional', [])
        return [self.replace_chars(d) for d in dimension_names]

    @property
    def dimensions_paths(self):
        return [self.get_property_path(value) for value in self.dimensions_names]

    @property
    def timestamp_path(self) -> str:
        return self.get_property_path(self.config['timestamp']['name'])

    @property
    def values(self):
        return self.config['values'].keys()

    @property
    def values_paths(self):
        return [self.get_property_path(value) for value in self.values]

    @property
    def target_types(self):
        return [self.get_property_path(value) for value in self.config['values'].values()]

    @property
    def measurement_names(self):
        return [self.replace_chars(self.config['measurement_names'].get(key, key)) for key in self.values]

    @property
    def count_records(self) -> bool:
        return self.config.get('count_records', False)

    @property
    def count_records_measurement_name(self) -> str:
        return self.replace_chars(self.config.get('count_records_measurement_name', 'count'))

    @property
    def static_what(self) -> bool:
        return self.config.get('static_what', True)

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


class PipelineException(click.ClickException):
    pass


class PipelineNotExistsException(PipelineException):
    pass

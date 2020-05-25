import click
import json
import os

from .. import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination
from ..source import KafkaSource


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
        # using 'anodot_agent_' + self.id as a default value in order not to break old configs
        self.override_source = config.pop(self.OVERRIDE_SOURCE,
                                          {KafkaSource.CONFIG_CONSUMER_GROUP: 'anodot_agent_' + self.id})

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.id)

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


class PipelineException(click.ClickException):
    pass


class PipelineNotExistsException(PipelineException):
    pass

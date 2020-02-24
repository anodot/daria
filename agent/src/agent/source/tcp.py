import click
import json

from .abstract_source import Source, SourceException
from agent.tools import infinite_retry, print_dicts, print_json, map_keys, if_validation_enabled
from .schemaless import SchemalessSource


class TCPSource(SchemalessSource):
    CONFIG_PORTS = 'conf.ports'

    VALIDATION_SCHEMA_FILE_NAME = 'tcp_server.json'

    def prompt(self, default_config, advanced=False):
        self.config[self.CONFIG_PORTS] = click.prompt('Ports', type=click.STRING,
                                                      value_proc=lambda x: x.split(','),
                                                      default=default_config.get(self.CONFIG_PORTS))
        self.prompt_data_format(default_config)
        if advanced:
            self.prompt_batch_size(default_config)

    def validate(self):
        self.validate_json()
        self.validate_connection()

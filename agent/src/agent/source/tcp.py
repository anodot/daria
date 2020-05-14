import click
import socket

from agent.tools import infinite_retry
from .schemaless import SchemalessSource


class TCPSource(SchemalessSource):
    CONFIG_PORTS = 'conf.ports'
    TEST_PIPELINE_FILENAME = 'test_tcp_server_jksrj322'

    VALIDATION_SCHEMA_FILE_NAME = 'tcp_server.json'

    @infinite_retry
    def prompt_ports(self, default_config):
        self.config[self.CONFIG_PORTS] = click.prompt('Port', type=click.STRING,
                                                      value_proc=lambda x: x.split(','),
                                                      default=default_config.get(self.CONFIG_PORTS))
        for port in self.config[self.CONFIG_PORTS]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('0.0.0.0', int(port)))

    def prompt(self, default_config, advanced=False):
        self.prompt_ports(default_config)

        self.prompt_data_format(default_config)
        if advanced:
            self.prompt_batch_size(default_config)
        return self.config

    def validate(self):
        self.validate_json()
        self.validate_connection()

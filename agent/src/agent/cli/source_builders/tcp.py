import click
import socket

from agent.tools import infinite_retry
from .schemaless import SchemalessSourceBuilder


class TCPSourceBuilder(SchemalessSourceBuilder):
    CONFIG_PORTS = 'conf.ports'

    @infinite_retry
    def prompt_ports(self, default_config):
        self.source.config[self.CONFIG_PORTS] = \
            click.prompt('Port', type=click.STRING, value_proc=lambda x: x.split(','),
                         default=default_config.get(self.CONFIG_PORTS))
        for port in self.source.config[self.CONFIG_PORTS]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('0.0.0.0', int(port)))

    def prompt(self, default_config, advanced=False):
        self.prompt_ports(default_config)
        self.prompt_data_format(default_config)
        if advanced:
            self.prompt_batch_size(default_config)
        self.source.set_config(self.source.config)
        return self.source

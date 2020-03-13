import click
import socket

from agent.tools import infinite_retry
from .schemaless import SchemalessSource


def accept_messages(connection):
    msg = ''
    while True:
        data = connection.recv(1024).decode()
        if not data:
            break
        split_messages = data.split('\n')
        msg += split_messages[0]
        if len(split_messages) > 1:
            print(msg)
            msg = split_messages[1]


def run_tcp_server(port: int):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            s.listen()
            while True:
                print(f'Accepting connections on port {port}')
                print('To stop the server and continue pipeline configuration press ctrl+C')
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    accept_messages(conn)
                print('Connection closed')
    except KeyboardInterrupt:
        print('Stopped')


class TCPSource(SchemalessSource):
    CONFIG_PORTS = 'conf.ports'
    TEST_PIPELINE_NAME = 'test_tcp_server_jksrj322'

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

        if click.confirm('Do you want to run a TCP server for testing the connection?'):
            run_tcp_server(int(self.config[self.CONFIG_PORTS][0]))

        self.prompt_data_format(default_config)
        if advanced:
            self.prompt_batch_size(default_config)
        return self.config

    def validate(self):
        self.validate_json()
        self.validate_connection()

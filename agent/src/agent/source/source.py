import click

from abc import ABC


class Source(ABC):
    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    def set_config(self, config):
        self.config = config

    # todo move
    def update_test_source_config(self, stage):
        for conf in stage['configuration']:
            if conf['name'] in self.config:
                conf['value'] = self.config[conf['name']]


class DirectorySource(Source):
    pass


class ElasticSource(Source):
    pass


class InfluxSource(Source):
    pass


class JDBCSource(Source):
    pass


class KafkaSource(Source):
    pass


class MongoSource(Source):
    pass


class SageSource(Source):
    pass


class TCPSource(Source):
    pass


class MonitoringSource(Source):
    pass


class SourceException(click.ClickException):
    pass


class SourceNotExists(SourceException):
    pass


class SourceConfigDeprecated(SourceException):
    pass


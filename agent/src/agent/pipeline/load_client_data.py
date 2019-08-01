import os
import json

from jsonschema import validate


definitions_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json_schema_definitions')


class LoadClientData:
    VALIDATION_SCHEMA_FILE_NAME = ''

    def __init__(self, client_config, edit=False):
        self.client_config = client_config
        self.edit = edit
        with open(os.path.join(definitions_dir, self.VALIDATION_SCHEMA_FILE_NAME + '.json'), 'r') as f:
            schema = json.load(f)
        if self.edit:
            schema['required'] = []
        validate(self.client_config, schema)
        client_config.pop('source', None)

    def load_dimensions(self):
        if type(self.client_config.get('dimensions')) == list:
            self.client_config['dimensions'] = {'required': [], 'optional': self.client_config['dimensions']}

    def load_value(self):
        if type(self.client_config.get('value')) == str:
            self.client_config['value'] = {'type': 'property', 'value': self.client_config['value']}

    def load(self):
        self.load_dimensions()
        self.load_value()
        return self.client_config


class MongoLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'mongo'


class KafkaLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'kafka'

    def load(self):
        self.load_dimensions()
        self.load_value()
        if 'timestamp' not in self.client_config and not self.edit:
            self.client_config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        return self.client_config


class InfluxLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'influx'

    def load_value(self):
        if type(self.client_config.get('value')) == list:
            self.client_config['value'] = {'type': 'property', 'values': self.client_config['value'], 'constant': '1'}
        elif str(self.client_config.get('value')).isnumeric():
            self.client_config['value'] = {'type': 'constant', 'values': [],
                                           'constant': str(self.client_config['value'])}


class JDBCLoadClientData(LoadClientData):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc'

    def load(self):
        return self.client_config


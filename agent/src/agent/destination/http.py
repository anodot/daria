import json
import os
import urllib.parse
import uuid

from agent.constants import ANODOT_API_URL, DATA_DIR


class HttpDestination:
    FILE = os.path.join(DATA_DIR, 'destination.json')
    TYPE = 'http'

    def __init__(self):
        self.config = {'config': {}, 'type': self.TYPE, 'host_id': self.generate_host_id()}

    @classmethod
    def generate_host_id(cls, length=10):
        return str(uuid.uuid4()).replace('-', '')[:length].upper()

    @classmethod
    def exists(cls):
        return os.path.isfile(cls.FILE)

    def load(self):
        if not self.exists():
            raise DestinationException('Destination wasn\'t configured')

        with open(self.FILE, 'r') as f:
            self.config = json.load(f)

        return self.config

    def update_url(self, token):
        self.config['config']['conf.resourceUrl'] = urllib.parse.urljoin(
            ANODOT_API_URL, f'api/v1/metrics?token={token}&protocol=anodot20')

    def save(self):
        with open(self.FILE, 'w') as f:
            json.dump(self.config, f)

    def enable_logs(self, enable=True):
        self.config['config']['conf.client.requestLoggingConfig.enableRequestLogging'] = enable

    def set_proxy(self, enable, uri='', username='', password=''):
        self.config['config']['conf.client.useProxy'] = enable
        if enable:
            self.config['config']['conf.client.proxy.uri'] = uri
            self.config['config']['conf.client.proxy.username'] = username
            self.config['config']['conf.client.proxy.password'] = password

    def get_proxy_url(self):
        return self.config['config'].get('conf.client.proxy.uri')

    def get_proxy_username(self):
        return self.config['config'].get('conf.client.proxy.username')


class DestinationException(Exception):
    pass

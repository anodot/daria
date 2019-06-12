import json
import os
import urllib.parse
import uuid

from agent.constants import ANODOT_API_URL, DATA_DIR


class HttpDestination:
    FILE = os.path.join(DATA_DIR, 'destination.json')
    TYPE = 'http'

    CONFIG_PROXY_USE = 'conf.client.useProxy'
    CONFIG_PROXY_USERNAME = 'conf.client.proxy.username'
    CONFIG_PROXY_PASSWORD = 'conf.client.proxy.password'
    CONFIG_PROXY_URI = 'conf.client.proxy.uri'
    CONFIG_RESOURCE_URL = 'conf.resourceUrl'
    CONFIG_ENABLE_REQUEST_LOGGING = 'conf.client.requestLoggingConfig.enableRequestLogging'

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
        self.config['config'][self.CONFIG_RESOURCE_URL] = urllib.parse.urljoin(
            ANODOT_API_URL, f'api/v1/metrics?token={token}&protocol=anodot20')

    def save(self):
        with open(self.FILE, 'w') as f:
            json.dump(self.config, f)

    def enable_logs(self, enable=True):
        self.config['config'][self.CONFIG_ENABLE_REQUEST_LOGGING] = enable

    def set_proxy(self, enable, uri='', username='', password=''):
        self.config['config'][self.CONFIG_PROXY_USE] = enable
        if enable:
            self.config['config'][self.CONFIG_PROXY_URI] = uri
            self.config['config'][self.CONFIG_PROXY_USERNAME] = username
            self.config['config'][self.CONFIG_PROXY_PASSWORD] = password

    def get_proxy_url(self):
        return self.config['config'].get(self.CONFIG_PROXY_URI)

    def get_proxy_username(self):
        return self.config['config'].get(self.CONFIG_PROXY_USERNAME)


class DestinationException(Exception):
    pass

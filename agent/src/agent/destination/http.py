import json
import os
import urllib.parse
import uuid
import requests

from agent.constants import ANODOT_API_URL, DATA_DIR, ENV_PROD
from urllib.parse import urlparse, urlunparse


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
        self.config = {}
        self.host_id = self.generate_host_id()

    def to_dict(self):
        return {'config': self.config, 'type': self.TYPE, 'host_id': self.host_id}

    @classmethod
    def generate_host_id(cls, length: int = 10) -> str:
        return str(uuid.uuid4()).replace('-', '')[:length].upper()

    @classmethod
    def exists(cls) -> bool:
        return os.path.isfile(cls.FILE)

    def load(self):
        if not self.exists():
            raise DestinationException('Destination wasn\'t configured')

        with open(self.FILE, 'r') as f:
            config = json.load(f)

        self.config = config['config']
        self.host_id = config['host_id']

        return config

    def update_url(self, token):
        self.config[self.CONFIG_RESOURCE_URL] = urllib.parse.urljoin(
            ANODOT_API_URL, f'api/v1/metrics?token={token}&protocol=anodot20')

    def save(self):
        try:
            self.validate()
        except requests.exceptions.RequestException as e:
            raise DestinationException(str(e))

        with open(self.FILE, 'w') as f:
            json.dump(self.to_dict(), f)

    def enable_logs(self, enable: bool = True):
        self.config[self.CONFIG_ENABLE_REQUEST_LOGGING] = enable

    def set_proxy(self, enable, uri='', username='', password=''):
        self.config[self.CONFIG_PROXY_USE] = enable
        if enable:
            self.config[self.CONFIG_PROXY_URI] = uri
            self.config[self.CONFIG_PROXY_USERNAME] = username
            self.config[self.CONFIG_PROXY_PASSWORD] = password

    def get_proxy_url(self):
        return self.config.get(self.CONFIG_PROXY_URI)

    def get_proxy_username(self):
        return self.config.get(self.CONFIG_PROXY_USERNAME)

    def validate(self) -> bool:
        if not ENV_PROD:
            return True
        proxies = {}
        if self.config[self.CONFIG_PROXY_USE]:
            proxy_parsed = urlparse(self.config[self.CONFIG_PROXY_URI])
            if self.config[self.CONFIG_PROXY_PASSWORD]:
                userpass = self.config[self.CONFIG_PROXY_USERNAME] + ':' + self.config[self.CONFIG_PROXY_PASSWORD]
                netloc = userpass + '@' + proxy_parsed.netloc
            else:
                netloc = proxy_parsed.netloc
            proxies['http'] = urlunparse((proxy_parsed.scheme, netloc, proxy_parsed.path, '', '', ''))
            proxies['https'] = proxies['http']
        result = requests.post(self.config[self.CONFIG_RESOURCE_URL], proxies=proxies)
        result.raise_for_status()
        return True


class DestinationException(Exception):
    pass

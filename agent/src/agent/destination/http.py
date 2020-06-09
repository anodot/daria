import click
import json
import os
import urllib.parse
import uuid
import requests

from typing import Dict, Optional
from agent.anodot_api_client import AnodotApiClient
from agent.constants import ANODOT_API_URL, DATA_DIR
from urllib.parse import urlparse, urlunparse
from agent.destination import Proxy
from result import Result, Ok, Err


class HttpDestination:
    FILE = os.path.join(DATA_DIR, 'destination.json')
    TYPE = 'http'

    CONFIG_PROXY_USE = 'conf.client.useProxy'
    CONFIG_PROXY_USERNAME = 'conf.client.proxy.username'
    CONFIG_PROXY_PASSWORD = 'conf.client.proxy.password'
    CONFIG_PROXY_URI = 'conf.client.proxy.uri'
    CONFIG_RESOURCE_URL = 'conf.resourceUrl'
    CONFIG_ENABLE_REQUEST_LOGGING = 'conf.client.requestLoggingConfig.enableRequestLogging'

    CONFIG_MONITORING_URL = 'monitoring_url'

    PROTOCOL_20 = 'anodot20'
    PROTOCOL_30 = 'anodot30'

    def __init__(self):
        self.config: Dict[str, any] = {self.CONFIG_PROXY_USE: False}
        self.host_id = self.generate_host_id()
        self.api_key = ''

    @staticmethod
    def get() -> Optional['HttpDestination']:
        if HttpDestination.exists():
            dest = HttpDestination()
            dest.__load()
            return dest
        return None

    @staticmethod
    def get_or_default() -> 'HttpDestination':
        dest = HttpDestination()
        if HttpDestination.exists():
            dest.__load()
        return dest

    def to_dict(self) -> dict:
        return {
            'config': self.config,
            'type': self.TYPE,
            'host_id': self.host_id,
            'api_key': self.api_key
        }

    @property
    def monitoring_url(self):
        return self.config[self.CONFIG_MONITORING_URL]

    @classmethod
    def generate_host_id(cls, length: int = 10) -> str:
        return str(uuid.uuid4()).replace('-', '')[:length].upper()

    @classmethod
    def exists(cls) -> bool:
        return os.path.isfile(cls.FILE)

    @property
    def url(self):
        return self.config.get('url', ANODOT_API_URL)

    @url.setter
    def url(self, value: str):
        self.config['url'] = value

    @property
    def token(self):
        return self.config.get('token', None)

    @token.setter
    def token(self, value: str):
        self.config['token'] = value

    def __load(self):
        with open(self.FILE) as f:
            config = json.load(f)
            self.config = config['config']
            self.host_id = config['host_id']
            self.api_key = config.get('api_key')

    def build_urls(self):
        if not self.token:
            raise DestinationException('Token is empty')
        if not self.url:
            raise DestinationException('Url is empty')
        self.config[self.CONFIG_RESOURCE_URL] = \
            urllib.parse.urljoin(self.url, f'api/v1/metrics?token={self.token}&protocol={self.PROTOCOL_20}')
        self.config[self.CONFIG_MONITORING_URL] = \
            urllib.parse.urljoin(self.url, f'api/v1/agents?token={self.token}')

    def save(self):
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

    def get_proxy_url(self) -> str:
        return self.config.get(self.CONFIG_PROXY_URI, '')

    def get_proxy_username(self) -> str:
        return self.config.get(self.CONFIG_PROXY_USERNAME, '')

    def get_proxy_password(self) -> str:
        return self.config.get(self.CONFIG_PROXY_PASSWORD, '')

    def get_proxy_configs(self) -> dict:
        proxies = dict()
        if self.config[self.CONFIG_PROXY_USE]:
            proxy_parsed = urlparse(self.get_proxy_url())
            netloc = proxy_parsed.netloc
            if self.get_proxy_password():
                netloc = self.get_proxy_username() + ':' + self.get_proxy_password() + '@' + netloc
            proxies['http'] = urlunparse((proxy_parsed.scheme, netloc, proxy_parsed.path, '', '', ''))
            proxies['https'] = proxies['http']
        return proxies

    def validate_token(self) -> bool:
        result = requests.post(self.config[self.CONFIG_RESOURCE_URL], proxies=self.get_proxy_configs(), timeout=5)
        result.raise_for_status()
        return True

    def validate_api_key(self) -> bool:
        if self.api_key:
            AnodotApiClient(self.api_key, self.get_proxy_configs(), base_url=self.url)
        return True

    def validate(self) -> bool:
        try:
            self.validate_token()
        except requests.HTTPError:
            raise DestinationException('Data collection token is invalid')
        try:
            self.validate_api_key()
        except requests.HTTPError:
            raise DestinationException('API key is invalid')
        return True


class DestinationException(click.ClickException):
    pass


def __build(
        destination: HttpDestination,
        data_collection_token: str = None,
        destination_url: str = None,
        access_key: str = None,
        proxy: Proxy = None,
        host_id: str = None,
) -> Result[HttpDestination, str]:
    if data_collection_token:
        destination.token = data_collection_token
    if destination_url:
        destination.url = destination_url
    if access_key:
        destination.api_key = access_key
    if proxy:
        destination.set_proxy(True, proxy.uri, proxy.username, proxy.password)
    if host_id:
        destination.host_id = host_id
    try:
        destination.build_urls()
    except DestinationException as e:
        return Err(e.message)
    try:
        destination.validate()
    except DestinationException as e:
        return Err(e.message)
    destination.save()
    return Ok(destination)


def create(
        data_collection_token: str,
        destination_url: str,
        access_key: str = None,
        proxy: Proxy = None,
        host_id: str = None,
) -> Result[HttpDestination, str]:
    return __build(HttpDestination(), data_collection_token, destination_url, access_key, proxy, host_id)


def edit(
        destination: HttpDestination,
        data_collection_token: str = None,
        destination_url: str = None,
        access_key: str = None,
        proxy: Proxy = None,
        host_id: str = None,
) -> Result[HttpDestination, str]:
    return __build(destination, data_collection_token, destination_url, access_key, proxy, host_id)

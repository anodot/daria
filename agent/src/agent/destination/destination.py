import urllib.parse
import uuid

from typing import Dict, Optional
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from agent.constants import ANODOT_API_URL
from agent.db import Entity
from agent.proxy import Proxy
from sqlalchemy import Column, Integer, String, JSON


class HttpDestination(Entity):
    __tablename__ = 'destinations'

    id = Column(Integer, primary_key=True)
    host_id = Column(String)
    access_key = Column(String)
    config = Column(MutableDict.as_mutable(JSON))

    pipelines = relationship('Pipeline', back_populates='destination')

    TYPE = 'http'
    STATUS_URL = 'api/v1/status'

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
        self.access_key = ''

    def to_dict(self) -> dict:
        return {
            'config': self.config,
            'type': self.TYPE,
            'host_id': self.host_id,
            'access_key': self.access_key
        }

    @classmethod
    def generate_host_id(cls, length: int = 10) -> str:
        return str(uuid.uuid4()).replace('-', '')[:length].upper()

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

    @property
    def resource_url(self) -> Optional[str]:
        return self.config.get(self.CONFIG_RESOURCE_URL)

    @resource_url.setter
    def resource_url(self, resource_url: str):
        self.config[self.CONFIG_RESOURCE_URL] = resource_url

    @property
    def monitoring_url(self) -> Optional[str]:
        return self.config.get(self.CONFIG_MONITORING_URL)

    @monitoring_url.setter
    def monitoring_url(self, monitoring_url: str):
        self.config[self.CONFIG_MONITORING_URL] = monitoring_url

    def enable_logs(self):
        self.config[self.CONFIG_ENABLE_REQUEST_LOGGING] = True

    def disable_logs(self):
        self.config[self.CONFIG_ENABLE_REQUEST_LOGGING] = False

    @property
    def proxy(self) -> Optional[Proxy]:
        if self.config[self.CONFIG_PROXY_USE]:
            return Proxy(
                self.config[self.CONFIG_PROXY_URI],
                self.config[self.CONFIG_PROXY_USERNAME],
                self.config[self.CONFIG_PROXY_PASSWORD],
            )
        return None

    @proxy.setter
    def proxy(self, proxy: Proxy):
        self.config[self.CONFIG_PROXY_USE] = True
        self.config[self.CONFIG_PROXY_URI] = proxy.uri
        self.config[self.CONFIG_PROXY_USERNAME] = proxy.username
        self.config[self.CONFIG_PROXY_PASSWORD] = proxy.password

    def get_proxy_url(self) -> str:
        return self.config.get(self.CONFIG_PROXY_URI, '')

    def get_proxy_username(self) -> str:
        return self.config.get(self.CONFIG_PROXY_USERNAME, '')


def build_urls(destination_url: str, data_collection_token: str) -> (str, str):
    resource_url = urllib.parse.urljoin(
        destination_url, f'api/v1/metrics?token={data_collection_token}&protocol={HttpDestination.PROTOCOL_20}')
    monitoring_url = urllib.parse.urljoin(destination_url, f'api/v1/agents?token={data_collection_token}')
    return resource_url, monitoring_url

import urllib.parse
import uuid

from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from agent.modules.constants import ANODOT_API_URL
from agent.modules.db import Entity
from agent.modules.proxy import Proxy
from sqlalchemy import Column, Integer, String, JSON, func, ForeignKey


class HttpDestination(Entity):
    __tablename__ = 'destinations'

    id = Column(Integer, primary_key=True)
    host_id = Column(String)
    access_key = Column(String)
    config = Column(MutableDict.as_mutable(JSON))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())

    auth_token = relationship("AuthenticationToken", cascade="delete", uselist=False)

    TYPE = 'http'
    STATUS_URL = 'api/v1/status'

    CONFIG_PROXY_USE = 'conf.client.useProxy'
    CONFIG_PROXY_USERNAME = 'conf.client.proxy.username'
    CONFIG_PROXY_PASSWORD = 'conf.client.proxy.password'
    CONFIG_PROXY_URI = 'conf.client.proxy.uri'
    CONFIG_ENABLE_REQUEST_LOGGING = 'conf.client.requestLoggingConfig.enableRequestLogging'

    CONFIG_MONITORING_URL = 'monitoring_url'

    PROTOCOL_20 = 'anodot20'
    PROTOCOL_30 = 'anodot30'

    def __init__(self):
        self.config: Dict[str, any] = {self.CONFIG_PROXY_USE: False}
        self.host_id = self.generate_host_id()
        self.access_key = None

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
        return \
            urllib.parse.urljoin(self.url, f'api/v1/metrics?token={self.token}&protocol={HttpDestination.PROTOCOL_20}')

    @property
    def monitoring_url(self) -> Optional[str]:
        return urllib.parse.urljoin(self.url, f'api/v1/agents?token={self.token}')

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


class AuthenticationToken(Entity):
    __tablename__ = 'authentication_tokens'

    id = Column(Integer, primary_key=True)
    destination_id = Column(Integer, ForeignKey('destinations.id'))
    authentication_token = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())

    destination = relationship('HttpDestination')

    EXPIRATION_PERIOD_IN_SECONDS = 24 * 60 * 60

    def __init__(self, destination_: HttpDestination, token: str):
        self.destination_id = destination_.id
        self.destination = destination_
        self.authentication_token = token
        self.created_at = datetime.now()

    def update(self, token: str):
        self.authentication_token = token
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        # leave 100 sec gap just to be sure we're not using expired token
        return (datetime.now() - self.created_at).seconds > self.EXPIRATION_PERIOD_IN_SECONDS - 100

import base64
import json
import urllib.parse
import uuid
import os

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
    CONFIG_USE_JKS_TRUSTSTORE = 'conf.client.tlsConfig.tlsEnabled'
    CONFIG_KEYSTORE_FILE_PATH = 'conf.client.tlsConfig.keyStoreFilePath'
    CONFIG_KEYSTORE_PASSWORD = 'conf.client.tlsConfig.keyStorePassword'
    CONFIG_TRUSTSTORE_FILE_PATH = 'conf.client.tlsConfig.trustStoreFilePath'
    CONFIG_TRUSTSTORE_PASSWORD = 'conf.client.tlsConfig.trustStorePassword'

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
    def use_jks_truststore(self):
        return self.config.get(self.CONFIG_USE_JKS_TRUSTSTORE, False)

    @use_jks_truststore.setter
    def use_jks_truststore(self, value=False):
        self.config[self.CONFIG_USE_JKS_TRUSTSTORE] = value
        self.config[self.CONFIG_KEYSTORE_FILE_PATH] = os.environ.get('JKS_KEYSTORE_FILE_PATH', '/data/truststore.jks')
        self.config[self.CONFIG_KEYSTORE_PASSWORD] = os.environ.get('JKS_KEYSTORE_PASSWORD', 'changeit')
        self.config[self.CONFIG_TRUSTSTORE_FILE_PATH] = os.environ.get('JKS_TRUSTSTORE_FILE_PATH', '/data/truststore.jks')
        self.config[self.CONFIG_TRUSTSTORE_PASSWORD] = os.environ.get('JKS_TRUSTSTORE_PASSWORD', 'changeit')

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
    def metrics_url(self) -> Optional[str]:
        return \
            urllib.parse.urljoin(self.url, f'api/v1/metrics?token={self.token}&protocol={HttpDestination.PROTOCOL_20}')

    def enable_logs(self):
        self.config[self.CONFIG_ENABLE_REQUEST_LOGGING] = True

    def disable_logs(self):
        self.config[self.CONFIG_ENABLE_REQUEST_LOGGING] = False

    @property
    def if_logs_enabled(self) -> bool:
        return self.config.get(self.CONFIG_ENABLE_REQUEST_LOGGING, False)

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
    def proxy(self, proxy: Optional[Proxy]):
        if proxy:
            self.config[self.CONFIG_PROXY_USE] = True
            self.config[self.CONFIG_PROXY_URI] = proxy.uri
            self.config[self.CONFIG_PROXY_USERNAME] = proxy.username
            self.config[self.CONFIG_PROXY_PASSWORD] = proxy.password
        else:
            self.config[self.CONFIG_PROXY_USE] = False
            self.config[self.CONFIG_PROXY_URI] = ''
            self.config[self.CONFIG_PROXY_USERNAME] = ''
            self.config[self.CONFIG_PROXY_PASSWORD] = ''

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

    EXPIRATION_PERIOD_IN_SECONDS = 24 * 60 * 60

    def __init__(self, destination_id: int, token: str):
        self.destination_id = destination_id
        self.authentication_token = token
        self.created_at = datetime.now()

    def update(self, token: str):
        self.authentication_token = token
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        res = base64.b64decode(self.authentication_token.split('.')[1] + '==')
        expiration_timestamp = json.loads(res)['exp']
        # leave 100 sec gap just to be sure we're not using expired token
        return expiration_timestamp < datetime.now().timestamp() - 100


class DummyHttpDestination(HttpDestination):
    def __init__(self):
        super().__init__()
        self.token = 'dummy_token'

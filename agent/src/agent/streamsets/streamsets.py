import sdc_client

from typing import List
from sqlalchemy import Column, Integer, String
from agent import streamsets
from sqlalchemy.orm import relationship
from agent.modules.db import Entity


class StreamSets(Entity, sdc_client.IStreamSets):
    __tablename__ = 'streamsets'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    username = Column(String)
    password = Column(String)
    agent_external_url = Column(String)
    preferred_type = Column(String, nullable=True)

    pipelines = relationship('Pipeline', back_populates='streamsets')

    def __init__(self, url: str, username: str, password: str, agent_external_url: str, preferred_type: str = None):
        self.url = url
        self.username = username
        self.password = password
        self.agent_external_url = agent_external_url
        self.preferred_type = preferred_type

    def get_id(self) -> int:
        return self.id

    def get_url(self) -> str:
        return self.url

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def get_preferred_type(self) -> str:
        return self.preferred_type

    def to_dict(self) -> dict:
        return {
            'url': self.url,
            'username': self.username,
            'password': self.password,
            'agent_external_url': self.agent_external_url,
            'preferred_type': self.preferred_type,
        }


class Provider(sdc_client.IStreamSetsProvider):
    def get(self, id_: int) -> StreamSets:
        return streamsets.repository.get(id_)

    def get_all(self) -> List[StreamSets]:
        return streamsets.repository.get_all()

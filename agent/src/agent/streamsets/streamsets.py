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

    pipelines = relationship('Pipeline', back_populates='streamsets')

    def __init__(self, url: str, username: str, password: str, agent_external_url: str):
        self.url = url
        self.username = username
        self.password = password
        self.agent_external_url = agent_external_url

    def get_id(self) -> int:
        return self.id

    def get_url(self) -> str:
        return self.url

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password


class Provider(sdc_client.IStreamSetsProvider):
    def get(self, id_: int) -> StreamSets:
        return streamsets.repository.get(id_)

    def get_all(self) -> List[StreamSets]:
        return streamsets.repository.get_all()

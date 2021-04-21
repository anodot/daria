from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from agent import source
from agent.data_extractor import cacti
from agent.modules.db import Entity
from agent.pipeline import Pipeline


class CactiCache(Entity):
    __tablename__ = 'cacti_cache'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    data = Column(JSON)
    expires_at = Column(DateTime)

    def __init__(self, pipeline_id: str, data: dict, expires_at):
        self.pipeline_id = pipeline_id
        self.data = data
        self.expires_at = expires_at


class CactiCacher:
    GRAPHS = 'graphs'
    HOSTS = 'hosts'

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.cache: Optional[CactiCache] = cacti.repository.get_cache(pipeline_)

    def _get(self, key: str):
        return self.cache.data[key]

    @property
    def graphs(self) -> dict:
        return self._get(self.GRAPHS)

    @property
    def hosts(self) -> dict:
        return self._get(self.HOSTS)

    @property
    def connection_string(self):
        return self.pipeline.source.config[source.CactiSource.MYSQL_CONNECTION_STRING]


def _new_expire(ttl_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=ttl_seconds)

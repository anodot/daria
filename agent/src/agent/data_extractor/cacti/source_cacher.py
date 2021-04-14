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
    VARIABLES = 'variables'
    GRAPHS = 'graphs'
    SOURCES = 'sources'
    HOSTS = 'hosts'

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.cache: Optional[CactiCache] = cacti.repository.get_cache(pipeline_)

    def _get(self, key: str):
        if self.cache is None:
            self._cache_data()
        elif datetime.now() >= self.cache.expires_at:
            self._update_cache()
        return self.cache.data[key]

    @property
    def sources(self) -> dict:
        return self._get(self.SOURCES)

    @property
    def variables(self) -> dict:
        return self._get(self.VARIABLES)

    @property
    def graphs(self) -> dict:
        return self._get(self.GRAPHS)

    @property
    def hosts(self) -> dict:
        return self._get(self.HOSTS)

    def _cache_data(self):
        self.cache = CactiCache(
            self.pipeline.name,
            self._fetch_data(),
            _new_expire(int(self.pipeline.source.cache_ttl))
        )
        cacti.repository.save_source_cache(self.cache)

    def _update_cache(self):
        self.cache.data = self._fetch_data()
        self.cache.expires_at = _new_expire(int(self.pipeline.source.cache_ttl))
        cacti.repository.save_source_cache(self.cache)

    def _fetch_data(self) -> dict:
        return {
            self.VARIABLES: cacti.repository.get_variables(self.connection_string),
            self.GRAPHS: cacti.repository.get_graphs(self.connection_string),
            self.SOURCES: cacti.repository.get_sources(self.connection_string),
            self.HOSTS: cacti.repository.get_hosts(self.connection_string),
        }

    @property
    def connection_string(self):
        return self.pipeline.source.config[source.CactiSource.MYSQL_CONNECTION_STRING]


def _new_expire(ttl_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=ttl_seconds)
